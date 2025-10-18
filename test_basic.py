"""
Basic Test Script for VCD + AGLA Combined Method
Tests core functionality without requiring LAVIS/BLIP-ITM

This is a simplified test that checks:
1. VCD noise addition
2. Logits combination
3. Sampling function import
"""

import torch
import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_vcd_noise():
    """Test VCD noise addition"""
    logger.info("=" * 60)
    logger.info("Test 1: VCD Noise Addition")
    logger.info("=" * 60)
    
    try:
        from utils.vcd_add_noise import add_diffusion_noise
        
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
        import traceback
        traceback.print_exc()
        return False


def test_logits_combination():
    """Test logits combination formula"""
    logger.info("=" * 60)
    logger.info("Test 2: Logits Combination")
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
        valid_vcd = final_vcd[final_vcd != -float('inf')]
        logger.info(f"VCD only: range [{valid_vcd.min():.3f}, {valid_vcd.max():.3f}]")
        
        # Test AGLA only
        agla_alpha = 1.0
        agla_beta = 0.5
        combined_agla = logits_original + agla_alpha * logits_agla
        cutoff = torch.log(torch.tensor(agla_beta)) + logits_original.max(dim=-1, keepdim=True).values
        final_agla = combined_agla.masked_fill(logits_original < cutoff, -float("inf"))
        
        assert final_agla.shape == logits_original.shape, "AGLA shape mismatch!"
        valid_agla = final_agla[final_agla != -float('inf')]
        logger.info(f"AGLA only: range [{valid_agla.min():.3f}, {valid_agla.max():.3f}]")
        
        # Test combined
        combined = (
            (1 + cd_alpha + agla_alpha) * logits_original
            - cd_alpha * logits_vcd
            + agla_alpha * logits_agla
        )
        cutoff = torch.log(torch.tensor(cd_beta)) + logits_original.max(dim=-1, keepdim=True).values
        final_combined = combined.masked_fill(logits_original < cutoff, -float("inf"))
        
        assert final_combined.shape == logits_original.shape, "Combined shape mismatch!"
        valid_combined = final_combined[final_combined != -float('inf')]
        logger.info(f"Combined: range [{valid_combined.min():.3f}, {valid_combined.max():.3f}]")
        
        # Test sampling
        probs = torch.nn.functional.softmax(final_combined, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        logger.info(f"Sampled token: {next_token.item()}")
        
        logger.info("✓ Logits combination test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"✗ Logits combination test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sampling_function():
    """Test sampling function import"""
    logger.info("=" * 60)
    logger.info("Test 3: Sampling Function")
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
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test that all required files exist"""
    logger.info("=" * 60)
    logger.info("Test 4: File Structure")
    logger.info("=" * 60)
    
    try:
        required_files = [
            'sample_vcd_agla.py',
            'llava_llama_combined.py',
            'run_combined_llava.py',
            'test_combined.py',
            'utils/__init__.py',
            'utils/vcd_add_noise.py',
            'utils/augmentation.py',
            'configs/default_params.yaml',
            'requirements.txt',
            'README.md',
            'QUICKSTART.md',
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                logger.warning(f"  Missing: {file}")
            else:
                logger.debug(f"  Found: {file}")
        
        if missing_files:
            logger.error(f"✗ Missing {len(missing_files)} files")
            return False
        else:
            logger.info(f"✓ All {len(required_files)} required files present")
            logger.info("✓ File structure test PASSED")
            return True
        
    except Exception as e:
        logger.error(f"✗ File structure test FAILED: {e}")
        return False


def run_basic_tests():
    """Run basic tests"""
    logger.info("\n" + "=" * 60)
    logger.info("VCD + AGLA Combined Method - Basic Test Suite")
    logger.info("=" * 60 + "\n")
    
    results = {}
    
    # Run tests
    results['file_structure'] = test_file_structure()
    print()
    
    results['vcd_noise'] = test_vcd_noise()
    print()
    
    results['logits_combination'] = test_logits_combination()
    print()
    
    results['sampling_function'] = test_sampling_function()
    print()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result is True else "✗ FAILED"
        logger.info(f"{test_name:25s}: {status}")
    
    logger.info("=" * 60)
    logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    logger.info("=" * 60)
    
    if failed > 0:
        logger.error("\n❌ Some tests failed. Please fix the issues before proceeding.")
        return False
    else:
        logger.info("\n✅ All basic tests passed!")
        logger.info("\nNote: AGLA augmentation test requires LAVIS to be installed.")
        logger.info("Run 'python test_combined.py' for full test suite (requires LAVIS).")
        return True


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)

