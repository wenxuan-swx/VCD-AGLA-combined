#!/usr/bin/env python
"""
Test script to verify AGLA functionality is working
"""

import sys
sys.path.insert(0, '/root/autodl-tmp/VCD/experiments')
sys.path.insert(0, '/root/autodl-tmp/COMBINED')

print("=" * 60)
print("Testing AGLA Functionality")
print("=" * 60)

# Test 1: Import LAVIS
print("\n1. Testing LAVIS imports...")
try:
    from lavis.models import load_model_and_preprocess
    from lavis.common.gradcam import getAttMap
    from lavis.models.blip_models.blip_image_text_matching import compute_gradcam
    print("   ✓ LAVIS imports successful")
except Exception as e:
    print(f"   ❌ LAVIS import failed: {e}")
    sys.exit(1)

# Test 2: Import augmentation
print("\n2. Testing augmentation module...")
try:
    from utils.augmentation import augmentation
    print("   ✓ Augmentation module imported")
except Exception as e:
    print(f"   ❌ Augmentation import failed: {e}")
    sys.exit(1)

# Test 3: Load BLIP-ITM model
print("\n3. Testing BLIP-ITM model loading...")
try:
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   Using device: {device}")
    
    model_itm, vis_processors, text_processors = load_model_and_preprocess(
        'blip_image_text_matching', 'large', device=device, is_eval=True
    )
    print(f"   ✓ BLIP-ITM model loaded successfully")
    print(f"   Model type: {type(model_itm).__name__}")
except Exception as e:
    print(f"   ❌ Model loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test augmentation function
print("\n4. Testing augmentation function...")
try:
    from PIL import Image
    import torch
    from torchvision import transforms
    
    # Create a dummy image
    dummy_img = Image.new('RGB', (384, 384), color='red')
    loader = transforms.Compose([transforms.ToTensor()])
    tensor_img = loader(dummy_img)
    
    # Prepare BLIP inputs
    image_blip = vis_processors["eval"](dummy_img).unsqueeze(0).to(device)
    question = "Is there a cat in the image?"
    tokenized_text = model_itm.tokenizer(question, return_tensors="pt").to(device)
    
    # Run augmentation
    augmented_img = augmentation(
        image_blip, question, tensor_img, 
        model_itm, tokenized_text, dummy_img
    )
    
    print(f"   ✓ Augmentation function works")
    print(f"   Input image size: {dummy_img.size}")
    print(f"   Augmented image size: {augmented_img.size}")
    
except Exception as e:
    print(f"   ❌ Augmentation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test VCD+AGLA sampling evolution
print("\n5. Testing VCD+AGLA sampling evolution...")
try:
    from sample_vcd_agla import evolve_vcd_agla_sampling
    evolve_vcd_agla_sampling()
    print("   ✓ Sampling function evolved successfully")
except Exception as e:
    print(f"   ❌ Sampling evolution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All AGLA functionality tests passed!")
print("=" * 60)
print("\nYou can now run:")
print("  - AGLA Only: python run_pope_combined.py --use-agla ...")
print("  - VCD+AGLA Combined: python run_pope_combined.py --use-vcd --use-agla ...")

