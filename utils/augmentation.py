"""
AGLA Image Augmentation Module
Generates augmented images using GradCAM-based attention masking

Copied and adapted from AGLA project: /root/autodl-tmp/AGLA/eval/augmentation.py
"""

import sys
import os

# Remove VCD/experiments from sys.path to avoid lavis import conflicts
_vcd_exp_path = '/root/autodl-tmp/VCD/experiments'
if _vcd_exp_path in sys.path:
    sys.path.remove(_vcd_exp_path)

import torch
import numpy as np
from lavis.common.gradcam import getAttMap
from torchvision import transforms
from lavis.models.blip_models.blip_image_text_matching import compute_gradcam
import logging

# Restore VCD/experiments to sys.path after lavis import
if _vcd_exp_path not in sys.path:
    sys.path.insert(0, _vcd_exp_path)

logger = logging.getLogger(__name__)


def augmentation(image, question, tensor_image, model, tokenized_text, raw_image):
    """
    Generate augmented image based on GradCAM attention from BLIP-ITM model.
    
    This function:
    1. Computes GradCAM attention map using BLIP-ITM
    2. Calculates ITC score to determine masking ratio
    3. Masks out low-attention regions
    4. Returns augmented PIL image
    
    Args:
        image (torch.Tensor): Preprocessed image for BLIP-ITM [1, 3, H, W]
        question (str): Text question/prompt
        tensor_image (torch.Tensor): Image tensor [3, 384, 384] for masking
        model: BLIP-ITM model
        tokenized_text: Tokenized text from BLIP tokenizer
        raw_image (PIL.Image): Original PIL image
        
    Returns:
        PIL.Image: Augmented image with attention-based masking
        
    Example:
        >>> from lavis.models import load_model_and_preprocess
        >>> model_itm, vis_processors, text_processors = load_model_and_preprocess(
        ...     "blip_image_text_matching", "large", device="cuda", is_eval=True
        ... )
        >>> augmented = augmentation(image_blip, question, tensor_img, 
        ...                          model_itm, tokenized_text, raw_img)
    """
    try:
        # Compute GradCAM
        with torch.set_grad_enabled(True):
            gradcams, _ = compute_gradcam(
                model=model,
                visual_input=image,
                text_input=question,
                tokenized_text=tokenized_text,
                block_num=6
            )
        
        # Extract gradcam values
        gradcams = [gradcam_[1] for gradcam_ in gradcams]
        gradcams1 = torch.stack(gradcams).reshape(image.size(0), -1)
        
        # Compute ITC score to determine masking ratio
        itc_score = model({"image": image, "text_input": question}, match_head='itc')
        ratio = 1 - itc_score / 2
        ratio = min(ratio, 1 - 10**(-5))
        
        # Resize and normalize image
        resized_img = raw_image.resize((384, 384))
        norm_img = np.float32(resized_img) / 255
        gradcam = gradcams1.reshape(24, 24)

        # Get attention map
        avg_gradcam = getAttMap(norm_img, gradcam.cpu().numpy(), blur=True, overlap=False)
        temp, _ = torch.sort(torch.tensor(avg_gradcam).reshape(-1), descending=True)
        cam1 = torch.tensor(avg_gradcam).unsqueeze(2)
        cam = torch.cat([cam1, cam1, cam1], dim=2)

        # Handle numerical stability: check for inf/nan and clamp ratio
        ratio = float(ratio.item() if torch.is_tensor(ratio) else ratio)
        ratio = max(0.0, min(ratio, 0.99999))  # Clamp to valid range

        # Calculate index safely
        total_pixels = 384 * 384
        mask_index = int(total_pixels * ratio)
        mask_index = min(mask_index, total_pixels - 1)  # Ensure within bounds

        # Check if temp has valid values
        if torch.isinf(temp).any() or torch.isnan(temp).any():
            # Fallback: use median threshold
            logger.warning("Invalid values in gradcam, using median threshold")
            threshold = torch.median(temp)
        else:
            threshold = temp[mask_index]

        # Apply mask
        mask = torch.where(cam < threshold, 0, 1)
        new_image = tensor_image.permute(1, 2, 0) * mask
        
        # Convert back to PIL image
        unloader = transforms.ToPILImage()
        imag = new_image.clone().permute(2, 0, 1)
        imag = unloader(imag)
        
        logger.debug(f"Generated augmented image with masking ratio {ratio:.3f}")
        return imag
        
    except Exception as e:
        logger.error(f"Error in augmentation: {e}")
        raise

