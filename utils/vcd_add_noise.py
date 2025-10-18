"""
VCD Noise Addition Module
Adds diffusion noise to images for Visual Contrastive Decoding

Copied and adapted from VCD project: /root/autodl-tmp/VCD/vcd_utils/vcd_add_noise.py
"""

import torch
import logging

logger = logging.getLogger(__name__)


def add_diffusion_noise(image_tensor, noise_step):
    """
    Add diffusion noise to an image tensor using DDPM-style noise schedule.
    
    Args:
        image_tensor (torch.Tensor): Input image tensor of shape [C, H, W]
        noise_step (int): Noise step from 0-999, higher means more noise
        
    Returns:
        torch.Tensor: Noisy image tensor of the same shape
        
    Example:
        >>> image = torch.randn(3, 224, 224)
        >>> noisy_image = add_diffusion_noise(image, noise_step=500)
    """
    try:
        num_steps = 1000  # Number of diffusion steps

        # Decide beta in each step (variance schedule)
        betas = torch.linspace(-6, 6, num_steps)
        betas = torch.sigmoid(betas) * (0.5e-2 - 1e-5) + 1e-5

        # Decide alphas in each step
        alphas = 1 - betas
        alphas_prod = torch.cumprod(alphas, dim=0)
        alphas_prod_p = torch.cat([torch.tensor([1]).float(), alphas_prod[:-1]], 0)  # p for previous
        alphas_bar_sqrt = torch.sqrt(alphas_prod)
        one_minus_alphas_bar_log = torch.log(1 - alphas_prod)
        one_minus_alphas_bar_sqrt = torch.sqrt(1 - alphas_prod)

        def q_x(x_0, t):
            """Forward diffusion process"""
            noise = torch.randn_like(x_0)
            alphas_t = alphas_bar_sqrt[t]
            alphas_1_m_t = one_minus_alphas_bar_sqrt[t]
            return (alphas_t * x_0 + alphas_1_m_t * noise)

        # Validate noise_step
        noise_step = int(noise_step)
        if noise_step < 0 or noise_step >= num_steps:
            logger.warning(f"noise_step {noise_step} out of range [0, {num_steps-1}], clipping")
            noise_step = max(0, min(noise_step, num_steps - 1))

        # Apply noise
        noisy_image = image_tensor.clone()
        image_tensor_cd = q_x(noisy_image, noise_step)
        
        logger.debug(f"Added diffusion noise at step {noise_step}")
        return image_tensor_cd
        
    except Exception as e:
        logger.error(f"Error adding diffusion noise: {e}")
        raise

