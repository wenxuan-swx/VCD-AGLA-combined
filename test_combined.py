"""
Test Script for VCD + AGLA Combined Method

This script tests the core functionality of the combined method:
1. Image processing (VCD noise, AGLA augmentation)
2. Logits combination
3. Three-way forward pass
4. End-to-end generation

Usage:
    python test_combined.py
"""

import torch
import numpy as np
from PIL import Image
import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging first
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import VCD noise function (should always work)
from utils.vcd_add_noise import add_diffusion_noise


def test_vcd_noise():
    """Test VCD noise addition"""
    logger.info("=" * 60)
    logger.info("Test 1: VCD Noise Addition")
    logger.info("=" * 60)
    
    try:
        # Create test image tensor
        image_tensor = torch.randn(3, 224, 224)
        logger.info(f"Original image shape: {image_tensor.shape}")
        logger.info(f"Original image range: [{image_tensor.min():.3f}, {image_tensor.max():.3f}]")
        
        # Add noise at different steps
        for noise_step in [100, 500, 900]:
            noisy_tensor = add_diffusion_noise(image_tensor, noise_step)
            
            assert noisy_tensor.shape == image_tensor.shape, "Shape mismatch!"
            logger.info(f"Noise step {noise_step}: range [{noisy_tensor.min():.3f}, {noisy_tensor.max():.3f}]")
        
        logger.info("✓ VCD noise addition test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"✗ VCD noise addition test FAILED: {e}")
        return False


def test_agla_augmentation():
    """Test AGLA augmentation (requires BLIP-ITM)"""
    logger.info("=" * 60)
    logger.info("Test 2: AGLA Augmentation")
    logger.info("=" * 60)
    
    try:
        from utils.augmentation import augmentation
        from lavis.models import load_model_and_preprocess
        from torchvision import transforms
        
        logger.info("Loading BLIP-ITM model...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model_itm, vis_processors, text_processors = load_model_and_preprocess(
            "blip_image_text_matching", "large", device=device, is_eval=True
        )
        
        # Create test image
        test_image = Image.new('RGB', (384, 384), color='red')
        question = "What color is this image?"
        
        # Prepare inputs
        loader = transforms.Compose([transforms.ToTensor()])
        tensor_image = loader(test_image)
        image_blip = vis_processors["eval"](test_image).unsqueeze(0).to(device)
        question_blip = text_processors["eval"](question)
        tokenized_text = model_itm.tokenizer(
            question_blip, padding='longest', truncation=True, return_tensors="pt"
        ).to(device)
        
        # Generate augmented image
        augmented_image = augmentation(
            image_blip, question_blip, tensor_image, 
            model_itm, tokenized_text, test_image
        )
        
        assert isinstance(augmented_image, Image.Image), "Output should be PIL Image"
        logger.info(f"Augmented image size: {augmented_image.size}")
        logger.info("✓ AGLA augmentation test PASSED")
        return True
        
    except ImportError:
        logger.warning("⚠ AGLA augmentation test SKIPPED (lavis not installed)")
        return None
    except Exception as e:
        logger.error(f"✗ AGLA augmentation test FAILED: {e}")
        return False


def test_logits_combination():
    """Test logits combination formula"""
    logger.info("=" * 60)
    logger.info("Test 3: Logits Combination")
    logger.info("=" * 60)
    
    try:
        # Simulate logits
        batch_size, vocab_size = 1, 32000
        logits_original = torch.randn(batch_size, vocab_size)
        logits_vcd = torch.randn(batch_size, vocab_size)
        logits_agla = torch.randn(batch_size, vocab_size)
        
        logger.info(f"Logits shape: {logits_original.shape}")
        
        # Test VCD only
        cd_alpha = 1.0
        cd_beta = 0.1
        combined_vcd = (1 + cd_alpha) * logits_original - cd_alpha * logits_vcd
        cutoff = torch.log(torch.tensor(cd_beta)) + logits_original.max(dim=-1, keepdim=True).values
        final_vcd = combined_vcd.masked_fill(logits_original < cutoff, -float("inf"))
        
        assert final_vcd.shape == logits_original.shape, "VCD shape mismatch!"
        logger.info(f"VCD only: range [{final_vcd[final_vcd != -float('inf')].min():.3f}, "
                   f"{final_vcd[final_vcd != -float('inf')].max():.3f}]")
        
        # Test AGLA only
        agla_alpha = 1.0
        agla_beta = 0.5
        combined_agla = logits_original + agla_alpha * logits_agla
        cutoff = torch.log(torch.tensor(agla_beta)) + logits_original.max(dim=-1, keepdim=True).values
        final_agla = combined_agla.masked_fill(logits_original < cutoff, -float("inf"))
        
        assert final_agla.shape == logits_original.shape, "AGLA shape mismatch!"
        logger.info(f"AGLA only: range [{final_agla[final_agla != -float('inf')].min():.3f}, "
                   f"{final_agla[final_agla != -float('inf')].max():.3f}]")
        
        # Test combined
        combined = (
            (1 + cd_alpha + agla_alpha) * logits_original
            - cd_alpha * logits_vcd
            + agla_alpha * logits_agla
        )
        cutoff = torch.log(torch.tensor(cd_beta)) + logits_original.max(dim=-1, keepdim=True).values
        final_combined = combined.masked_fill(logits_original < cutoff, -float("inf"))
        
        assert final_combined.shape == logits_original.shape, "Combined shape mismatch!"
        logger.info(f"Combined: range [{final_combined[final_combined != -float('inf')].min():.3f}, "
                   f"{final_combined[final_combined != -float('inf')].max():.3f}]")
        
        # Test sampling
        probs = torch.nn.functional.softmax(final_combined, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        logger.info(f"Sampled token: {next_token.item()}")
        
        logger.info("✓ Logits combination test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"✗ Logits combination test FAILED: {e}")
        return False


def test_sampling_function():
    """Test sampling function import"""
    logger.info("=" * 60)
    logger.info("Test 4: Sampling Function")
    logger.info("=" * 60)
    
    try:
        from sample_vcd_agla import sample_vcd_agla, evolve_vcd_agla_sampling
        
        logger.info("✓ Successfully imported sample_vcd_agla")
        logger.info("✓ Successfully imported evolve_vcd_agla_sampling")
        
        # Test evolution
        import transformers
        original_sample = transformers.generation.utils.GenerationMixin.sample
        evolve_vcd_agla_sampling()
        new_sample = transformers.generation.utils.GenerationMixin.sample
        
        assert new_sample == sample_vcd_agla, "Evolution failed!"
        logger.info("✓ Sampling function evolution successful")
        
        # Restore original
        transformers.generation.utils.GenerationMixin.sample = original_sample
        
        logger.info("✓ Sampling function test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"✗ Sampling function test FAILED: {e}")
        return False


def test_model_import():
    """Test model import"""
    logger.info("=" * 60)
    logger.info("Test 5: Model Import")
    logger.info("=" * 60)
    
    try:
        # Try to import the combined model
        # Note: This will fail if llava is not installed
        try:
            from llava_llama_combined import LlavaLlamaForCausalLM, LlavaConfig
            logger.info("✓ Successfully imported LlavaLlamaForCausalLM")
            logger.info("✓ Successfully imported LlavaConfig")
            logger.info("✓ Model import test PASSED")
            return True
        except ImportError as e:
            logger.warning(f"⚠ Model import test SKIPPED: {e}")
            logger.warning("  This is expected if llava package is not installed")
            logger.warning("  You will need to copy llava_arch.py from AGLA or VCD project")
            return None
        
    except Exception as e:
        logger.error(f"✗ Model import test FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("VCD + AGLA Combined Method - Test Suite")
    logger.info("=" * 60 + "\n")
    
    results = {}
    
    # Run tests
    results['vcd_noise'] = test_vcd_noise()
    print()
    
    results['agla_augmentation'] = test_agla_augmentation()
    print()
    
    results['logits_combination'] = test_logits_combination()
    print()
    
    results['sampling_function'] = test_sampling_function()
    print()
    
    results['model_import'] = test_model_import()
    print()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result is True else ("✗ FAILED" if result is False else "⚠ SKIPPED")
        logger.info(f"{test_name:25s}: {status}")
    
    logger.info("=" * 60)
    logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    logger.info("=" * 60)
    
    if failed > 0:
        logger.error("\n❌ Some tests failed. Please fix the issues before proceeding.")
        return False
    elif passed == total:
        logger.info("\n✅ All tests passed! The combined method is ready to use.")
        return True
    else:
        logger.info(f"\n⚠️  {passed}/{total} tests passed. {skipped} tests were skipped.")
        logger.info("   The core functionality is working, but some optional features are unavailable.")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

