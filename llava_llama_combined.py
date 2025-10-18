"""
Modified LLaVA LLaMA Model for VCD + AGLA Combined Method

This module extends the standard LLaVA model to support three image inputs:
1. images: Original images
2. images_cd: VCD noisy images
3. images_agla: AGLA augmented images

Key additions:
- prepare_inputs_for_generation_agla() method for AGLA image input
- Support for images_agla parameter in forward()
- Support for agla_alpha and agla_beta parameters

Based on: /root/autodl-tmp/AGLA/llava/model/language_model/llava_llama.py
"""

import sys
from typing import List, Optional, Tuple, Union

import torch
import torch.nn as nn
from torch.nn import CrossEntropyLoss

from transformers import AutoConfig, AutoModelForCausalLM, \
                         LlamaConfig, LlamaModel, LlamaForCausalLM

from transformers.modeling_outputs import CausalLMOutputWithPast
import logging

logger = logging.getLogger(__name__)

# Note: This file assumes you have the LLaVA architecture modules available
# You may need to copy llava_arch.py and related files from the AGLA or VCD project
# Or install the llava package if available

try:
    # Try to import from installed llava package
    from llava.model.llava_arch import LlavaMetaModel, LlavaMetaForCausalLM
except ImportError:
    logger.warning("Could not import LlavaMetaModel and LlavaMetaForCausalLM. "
                   "Please ensure llava package is installed or copy the required files.")
    # Fallback: you would need to copy these from AGLA/llava/model/llava_arch.py
    raise


class LlavaConfig(LlamaConfig):
    """LLaVA model configuration"""
    model_type = "llava"


class LlavaLlamaModel(LlavaMetaModel, LlamaModel):
    """LLaVA LLaMA model with vision encoder"""
    config_class = LlavaConfig

    def __init__(self, config: LlamaConfig):
        super(LlavaLlamaModel, self).__init__(config)


class LlavaLlamaForCausalLM(LlamaForCausalLM, LlavaMetaForCausalLM):
    """
    LLaVA LLaMA model for causal language modeling with VCD+AGLA support.
    
    This model extends the standard LLaVA to support three types of image inputs
    for three-way contrastive decoding.
    """
    config_class = LlavaConfig

    def __init__(self, config):
        super(LlamaForCausalLM, self).__init__(config)
        self.model = LlavaLlamaModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()

    def get_model(self):
        return self.model

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        images: Optional[torch.FloatTensor] = None,
        images_cd: Optional[torch.FloatTensor] = None,
        images_agla: Optional[torch.FloatTensor] = None,
        cd_beta: Optional[float] = None,
        cd_alpha: Optional[float] = None,
        agla_beta: Optional[float] = None,
        agla_alpha: Optional[float] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, CausalLMOutputWithPast]:
        """
        Forward pass with support for three image inputs.
        
        Args:
            images: Original images
            images_cd: VCD noisy images (optional)
            images_agla: AGLA augmented images (optional)
            cd_alpha: VCD contrast strength
            cd_beta: VCD plausibility threshold
            agla_alpha: AGLA enhancement strength
            agla_beta: AGLA plausibility threshold
        """
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        # Prepare inputs with multimodal embeddings
        input_ids, attention_mask, past_key_values, inputs_embeds, labels = \
            self.prepare_inputs_labels_for_multimodal(
                input_ids, attention_mask, past_key_values, labels, images
            )

        # Forward through language model
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict
        )

        hidden_states = outputs[0]
        logits = self.lm_head(hidden_states)

        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            # Flatten the tokens
            loss_fct = CrossEntropyLoss()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            shift_labels = shift_labels.view(-1)
            # Enable model/pipeline parallelism
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)

        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    def prepare_inputs_for_generation(
        self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, **kwargs
    ):
        """Prepare inputs for generation with original images"""
        if past_key_values:
            input_ids = input_ids[:, -1:]

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
                "images": kwargs.get("images", None),
            }
        )
        return model_inputs

    def prepare_inputs_for_generation_cd(
        self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, **kwargs
    ):
        """
        Prepare inputs for generation with VCD noisy images.
        
        This method uses images_cd instead of images for the VCD branch.
        """
        if past_key_values:
            input_ids = input_ids[:, -1:]

        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
                "images": kwargs.get("images_cd", None),  # Use VCD noisy images
            }
        )
        return model_inputs

    def prepare_inputs_for_generation_agla(
        self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, **kwargs
    ):
        """
        Prepare inputs for generation with AGLA augmented images.
        
        This method uses images_agla instead of images for the AGLA branch.
        """
        if past_key_values:
            input_ids = input_ids[:, -1:]

        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
                "images": kwargs.get("images_agla", None),  # Use AGLA augmented images
            }
        )
        return model_inputs


# Register the model
AutoConfig.register("llava", LlavaConfig)
AutoModelForCausalLM.register(LlavaConfig, LlavaLlamaForCausalLM)

