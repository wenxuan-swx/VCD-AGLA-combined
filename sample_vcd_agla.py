"""
VCD + AGLA Combined Sampling Function
Three-way Contrastive Decoding for Mitigating Object Hallucinations

This module implements the combined sampling strategy that uses:
1. Original image logits
2. VCD noisy image logits (to suppress statistical bias)
3. AGLA augmented image logits (to enhance visual understanding)

Combined formula:
    final_logits = (1 + cd_alpha + agla_alpha) * logits_original
                   - cd_alpha * logits_noisy
                   + agla_alpha * logits_augmented
"""

import copy
import warnings
from typing import Optional, List, Union

import torch
import torch.distributed as dist
from torch import nn

from transformers.generation.logits_process import LogitsProcessorList
from transformers.generation.stopping_criteria import (
    StoppingCriteriaList,
    validate_stopping_criteria,
)
import transformers
from transformers.generation.utils import SampleOutput
import logging

logger = logging.getLogger(__name__)


def sample_vcd_agla(
    self,
    input_ids: torch.LongTensor,
    logits_processor: Optional[LogitsProcessorList] = None,
    stopping_criteria: Optional[StoppingCriteriaList] = None,
    logits_warper: Optional[LogitsProcessorList] = None,
    max_length: Optional[int] = None,
    pad_token_id: Optional[int] = None,
    eos_token_id: Optional[Union[int, List[int]]] = None,
    output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None,
    output_scores: Optional[bool] = None,
    return_dict_in_generate: Optional[bool] = None,
    synced_gpus: bool = False,
    streamer: Optional["BaseStreamer"] = None,
    **model_kwargs,
) -> Union[SampleOutput, torch.LongTensor]:
    """
    Three-way contrastive decoding sampling function.
    
    Args:
        input_ids: Input token IDs
        model_kwargs: Should contain:
            - images: Original images
            - images_cd: VCD noisy images (optional)
            - images_agla: AGLA augmented images (optional)
            - cd_alpha: VCD contrast strength (default: 1.0)
            - cd_beta: VCD plausibility threshold (default: 0.1)
            - agla_alpha: AGLA enhancement strength (default: 1.0)
            - agla_beta: AGLA plausibility threshold (default: 0.5)
    
    Returns:
        Generated token IDs
    """
    # Initialize processors and criteria
    logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
    stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
    
    if max_length is not None:
        warnings.warn(
            "`max_length` is deprecated in this function, use"
            " `stopping_criteria=StoppingCriteriaList(MaxLengthCriteria(max_length=max_length))` instead.",
            UserWarning,
        )
        stopping_criteria = validate_stopping_criteria(stopping_criteria, max_length)
    
    logits_warper = logits_warper if logits_warper is not None else LogitsProcessorList()
    pad_token_id = pad_token_id if pad_token_id is not None else self.generation_config.pad_token_id
    eos_token_id = eos_token_id if eos_token_id is not None else self.generation_config.eos_token_id

    if isinstance(eos_token_id, int):
        eos_token_id = [eos_token_id]
    eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device) if eos_token_id is not None else None
    
    output_scores = output_scores if output_scores is not None else self.generation_config.output_scores
    output_attentions = (
        output_attentions if output_attentions is not None else self.generation_config.output_attentions
    )
    output_hidden_states = (
        output_hidden_states if output_hidden_states is not None else self.generation_config.output_hidden_states
    )
    return_dict_in_generate = (
        return_dict_in_generate
        if return_dict_in_generate is not None
        else self.generation_config.return_dict_in_generate
    )

    # Check which methods to use
    use_vcd = model_kwargs.get("images_cd") is not None
    use_agla = model_kwargs.get("images_agla") is not None
    
    logger.info(f"Three-way decoding: VCD={use_vcd}, AGLA={use_agla}")
    
    # Create separate model_kwargs for VCD and AGLA
    model_kwargs_vcd = model_kwargs.copy() if use_vcd else None
    model_kwargs_agla = model_kwargs.copy() if use_agla else None
    
    # Get parameters
    cd_alpha = model_kwargs.get("cd_alpha", 1.0)
    cd_beta = model_kwargs.get("cd_beta", 0.1)
    agla_alpha = model_kwargs.get("agla_alpha", 1.0)
    agla_beta = model_kwargs.get("agla_beta", 0.5)
    
    logger.info(f"Parameters: cd_alpha={cd_alpha}, cd_beta={cd_beta}, "
                f"agla_alpha={agla_alpha}, agla_beta={agla_beta}")
    
    # Initialize attention / hidden states / scores tuples
    scores = () if (return_dict_in_generate and output_scores) else None
    decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
    cross_attentions = () if (return_dict_in_generate and output_attentions) else None
    decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None

    # Keep track of which sequences are already finished
    unfinished_sequences = torch.ones(input_ids.shape[0], dtype=torch.long, device=input_ids.device)
    this_peer_finished = False

    # Auto-regressive generation loop
    step = 0
    while True:
        if synced_gpus:
            this_peer_finished_flag = torch.tensor(0.0 if this_peer_finished else 1.0).to(input_ids.device)
            dist.all_reduce(this_peer_finished_flag, op=dist.ReduceOp.SUM)
            if this_peer_finished_flag.item() == 0.0:
                break

        # ========== 1. Original image forward pass ==========
        model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
        outputs = self(
            **model_inputs,
            return_dict=True,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
        )

        if synced_gpus and this_peer_finished:
            continue

        next_token_logits_original = outputs.logits[:, -1, :]

        # ========== 2. VCD: Noisy image forward pass ==========
        next_token_logits_vcd = None
        if use_vcd:
            model_inputs_vcd = self.prepare_inputs_for_generation_cd(input_ids, **model_kwargs_vcd)
            outputs_vcd = self(
                **model_inputs_vcd,
                return_dict=True,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
            )
            next_token_logits_vcd = outputs_vcd.logits[:, -1, :]

        # ========== 3. AGLA: Augmented image forward pass ==========
        next_token_logits_agla = None
        if use_agla:
            model_inputs_agla = self.prepare_inputs_for_generation_agla(input_ids, **model_kwargs_agla)
            outputs_agla = self(
                **model_inputs_agla,
                return_dict=True,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
            )
            next_token_logits_agla = outputs_agla.logits[:, -1, :]

        # ========== 4. Combine logits ==========
        if use_vcd and use_agla:
            # Three-way contrastive decoding
            combined_logits = (
                (1 + cd_alpha + agla_alpha) * next_token_logits_original
                - cd_alpha * next_token_logits_vcd
                + agla_alpha * next_token_logits_agla
            )
            
            # Apply plausibility constraint (using VCD's beta)
            cutoff = torch.log(torch.tensor(cd_beta)) + next_token_logits_original.max(dim=-1, keepdim=True).values
            final_logits = combined_logits.masked_fill(next_token_logits_original < cutoff, -float("inf"))
            
        elif use_vcd:
            # VCD only
            combined_logits = (1 + cd_alpha) * next_token_logits_original - cd_alpha * next_token_logits_vcd
            cutoff = torch.log(torch.tensor(cd_beta)) + next_token_logits_original.max(dim=-1, keepdim=True).values
            final_logits = combined_logits.masked_fill(next_token_logits_original < cutoff, -float("inf"))
            
        elif use_agla:
            # AGLA only
            combined_logits = next_token_logits_original + agla_alpha * next_token_logits_agla
            cutoff = torch.log(torch.tensor(agla_beta)) + next_token_logits_original.max(dim=-1, keepdim=True).values
            final_logits = combined_logits.masked_fill(next_token_logits_original < cutoff, -float("inf"))
            
        else:
            # Standard decoding
            final_logits = next_token_logits_original

        # ========== 5. Apply logits processing and sampling ==========
        final_logits = logits_processor(input_ids, final_logits)
        final_logits = logits_warper(input_ids, final_logits)

        # Sample next token
        probs = nn.functional.softmax(final_logits, dim=-1)
        next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

        # ========== 6. Update sequences ==========
        if eos_token_id is not None:
            if pad_token_id is None:
                raise ValueError("If `eos_token_id` is defined, make sure that `pad_token_id` is defined.")
            next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)

        # Update input_ids
        input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)

        if streamer is not None:
            streamer.put(next_tokens.cpu())

        # Store scores, attentions and hidden_states when required
        if return_dict_in_generate:
            if output_scores:
                scores += (final_logits,)
            if output_attentions:
                decoder_attentions += (
                    (outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,)
                )
                if self.config.is_encoder_decoder:
                    cross_attentions += (outputs.cross_attentions,)
            if output_hidden_states:
                decoder_hidden_states += (
                    (outputs.decoder_hidden_states,)
                    if self.config.is_encoder_decoder
                    else (outputs.hidden_states,)
                )

        # Update model_kwargs
        model_kwargs = self._update_model_kwargs_for_generation(
            outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder
        )

        if use_vcd:
            model_kwargs_vcd = self._update_model_kwargs_for_generation(
                outputs_vcd, model_kwargs_vcd, is_encoder_decoder=self.config.is_encoder_decoder
            )

        if use_agla:
            model_kwargs_agla = self._update_model_kwargs_for_generation(
                outputs_agla, model_kwargs_agla, is_encoder_decoder=self.config.is_encoder_decoder
            )

        # Check if finished
        if eos_token_id_tensor is not None:
            unfinished_sequences = unfinished_sequences.mul(
                next_tokens.tile(eos_token_id_tensor.shape[0], 1).ne(eos_token_id_tensor.unsqueeze(1)).prod(dim=0)
            )
            if unfinished_sequences.max() == 0:
                this_peer_finished = True

        if stopping_criteria(input_ids, scores):
            this_peer_finished = True

        if this_peer_finished and not synced_gpus:
            break
        
        step += 1

    if streamer is not None:
        streamer.end()

    if return_dict_in_generate:
        return SampleOutput(
            sequences=input_ids,
            scores=scores,
            attentions=decoder_attentions,
            hidden_states=decoder_hidden_states,
        )
    else:
        return input_ids


def evolve_vcd_agla_sampling():
    """
    Replace transformers' default sampling function with VCD+AGLA combined version.

    Call this function before using the model to enable three-way contrastive decoding.

    Example:
        >>> from sample_vcd_agla import evolve_vcd_agla_sampling
        >>> evolve_vcd_agla_sampling()
        >>> # Now model.generate() will use the combined sampling
    """
    transformers.generation.utils.GenerationMixin.sample = sample_vcd_agla
    logger.info("Evolved sampling function to VCD+AGLA three-way contrastive decoding")


def evolve_vcd_agla_sampling_qwenvl():
    """
    Replace transformers' default sampling function with VCD+AGLA combined version for Qwen-VL.

    This is the same as evolve_vcd_agla_sampling() but with a clearer name for Qwen-VL usage.

    Call this function before using the Qwen-VL model to enable three-way contrastive decoding.

    Example:
        >>> from sample_vcd_agla import evolve_vcd_agla_sampling_qwenvl
        >>> evolve_vcd_agla_sampling_qwenvl()
        >>> # Now Qwen-VL model.generate() will use the combined sampling
    """
    transformers.generation.utils.GenerationMixin.sample = sample_vcd_agla
    # Also set _sample for newer transformers versions
    transformers.generation.utils.GenerationMixin._sample = sample_vcd_agla
    logger.info("Evolved Qwen-VL sampling function to VCD+AGLA three-way contrastive decoding")

