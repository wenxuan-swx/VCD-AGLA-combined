"""
VCD + AGLA Combined Evaluation Script for Qwen-VL

This script combines VCD and AGLA methods for hallucination reduction on Qwen-VL model.
Supports three-way contrastive decoding: original image, VCD noisy image, and AGLA augmented image.

Usage:
    # Baseline
    python run_qwenvl_combined.py --model-path /path/to/qwen-vl --question-file pope.json --answers-file output.jsonl

    # VCD + AGLA Combined
    python run_qwenvl_combined.py --model-path /path/to/qwen-vl --question-file pope.json --answers-file output.jsonl \\
        --use-vcd --use-agla --cd-alpha 1.0 --cd-beta 0.1 --noise-step 500 --agla-alpha 1.0 --agla-beta 0.5
"""

import argparse
import json
from tqdm import tqdm
import sys
import os
import torch
from PIL import Image
from transformers import set_seed, AutoTokenizer

# Add COMBINED path first (highest priority) to ensure we use COMBINED's Qwen_VL
sys.path.insert(0, '/root/autodl-tmp/COMBINED')

# Import Qwen-VL from COMBINED directory
from Qwen_VL.modeling_qwen import QWenLMHeadModel

# Import VCD+AGLA sampling
from sample_vcd_agla import evolve_vcd_agla_sampling_qwenvl

# Import utilities
from utils.vcd_add_noise import add_diffusion_noise

# Try to import AGLA components
try:
    from lavis.models import load_model_and_preprocess
    from torchvision import transforms
    from utils.augmentation import augmentation
    AGLA_AVAILABLE = True
except Exception as e:
    print(f"Warning: AGLA not available: {e}")
    AGLA_AVAILABLE = False


def eval_model(args):
    """Main evaluation function"""
    # Evolve sampling to VCD+AGLA for Qwen-VL
    evolve_vcd_agla_sampling_qwenvl()
    print("✓ Evolved Qwen-VL sampling function to VCD+AGLA three-way contrastive decoding")
    
    # Load Qwen-VL model
    model_path = os.path.expanduser(args.model_path)
    model_name = 'qwen-vl'
    print(f"Loading Qwen-VL model from {model_path}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.padding_side = 'left'
    tokenizer.pad_token_id = tokenizer.eod_id
    
    model = QWenLMHeadModel.from_pretrained(
        model_path,
        device_map="cuda",
        trust_remote_code=True
    ).eval()
    
    # Load BLIP-ITM if AGLA is enabled
    model_itm = None
    vis_processors = None
    text_processors = None
    loader = None
    
    if args.use_agla:
        if not AGLA_AVAILABLE:
            print("ERROR: AGLA requested but not available. Please install LAVIS:")
            print("  pip install salesforce-lavis")
            sys.exit(1)
        
        print("Loading BLIP-ITM model for AGLA...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model_itm, vis_processors, text_processors = load_model_and_preprocess(
            "blip_image_text_matching", "base", device=device, is_eval=True
        )
        model_itm = model_itm.half()
        model_itm.eval()
        loader = transforms.Compose([transforms.ToTensor()])
        print("✓ BLIP-ITM loaded in fp16 mode")
    
    # Load questions
    questions = [json.loads(q) for q in open(os.path.expanduser(args.question_file), "r")]
    
    # Prepare output file
    answers_file = os.path.expanduser(args.answers_file)
    os.makedirs(os.path.dirname(answers_file) if os.path.dirname(answers_file) else '.', exist_ok=True)
    ans_file = open(answers_file, "w")
    
    print(f"\nStarting evaluation:")
    print(f"  Questions: {len(questions)}")
    print(f"  VCD: {args.use_vcd}")
    print(f"  AGLA: {args.use_agla}")
    if args.use_vcd:
        print(f"  VCD params: alpha={args.cd_alpha}, beta={args.cd_beta}, noise_step={args.noise_step}")
    if args.use_agla:
        print(f"  AGLA params: alpha={args.agla_alpha}, beta={args.agla_beta}")
    print()
    
    # Process each question
    for line in tqdm(questions, desc="Evaluating"):
        idx = line["question_id"]
        image_file = line["image"]
        question = line["text"]
        
        image_path = os.path.join(args.image_folder, image_file)
        
        # Load image
        try:
            raw_image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_file}: {e}")
            continue
        
        # Prepare original image tensor for Qwen-VL
        image_tensor = model.transformer.visual.image_transform(raw_image).unsqueeze(0).to(model.device)
        
        # Prepare VCD noisy image
        image_tensor_vcd = None
        if args.use_vcd:
            image_tensor_vcd = add_diffusion_noise(image_tensor, args.noise_step)
        
        # Prepare AGLA augmented image
        image_tensor_agla = None
        if args.use_agla and model_itm is not None:
            try:
                tensor_image = loader(raw_image.resize((384, 384)))
                image_blip = vis_processors["eval"](raw_image).unsqueeze(0).to('cuda').half()
                question_blip = text_processors["eval"](question)
                tokenized_text = model_itm.tokenizer(
                    question_blip, padding='longest', truncation=True, return_tensors="pt"
                ).to('cuda')
                
                with torch.no_grad():
                    augmented_image = augmentation(
                        image_blip, question_blip, tensor_image,
                        model_itm, tokenized_text, raw_image
                    )
                
                # Clean up intermediate tensors
                del image_blip, tensor_image, tokenized_text
                torch.cuda.empty_cache()
                
                # Process augmented image for Qwen-VL
                image_tensor_agla = model.transformer.visual.image_transform(augmented_image).unsqueeze(0).to(model.device)
            except Exception as e:
                print(f"Warning: Failed to generate AGLA image for question {idx}: {e}")
                image_tensor_agla = None
        
        # Prepare question for Qwen-VL
        question_prompt = '<img>{}</img>{} Answer:'.format(image_path, question)
        input_ids = tokenizer([question_prompt], return_tensors='pt', padding='longest')
        
        # Generate
        with torch.inference_mode():
            pred = model.generate(
                input_ids=input_ids.input_ids.cuda(),
                attention_mask=input_ids.attention_mask.cuda(),
                do_sample=True,
                max_new_tokens=20,
                min_new_tokens=1,
                length_penalty=1,
                num_return_sequences=1,
                output_hidden_states=True,
                use_cache=True,
                pad_token_id=tokenizer.eod_id,
                eos_token_id=tokenizer.eod_id,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                images=image_tensor,
                images_cd=image_tensor_vcd,
                images_agla=image_tensor_agla,
                cd_alpha=args.cd_alpha,
                cd_beta=args.cd_beta,
                agla_alpha=args.agla_alpha,
                agla_beta=args.agla_beta,
            )
        
        # Decode output
        outputs = [
            tokenizer.decode(_[input_ids.input_ids.size(1):].cpu(),
                           skip_special_tokens=True).strip() for _ in pred
        ][0]
        outputs = outputs.strip()
        
        # Save answer
        ans_file.write(json.dumps({
            "question_id": idx,
            "prompt": question_prompt,
            "text": outputs,
            "model_id": model_name,
            "image": image_file,
            "metadata": {}
        }) + "\n")
        ans_file.flush()
        
        # Clean up tensors to free memory
        del image_tensor, pred
        if image_tensor_vcd is not None:
            del image_tensor_vcd
        if image_tensor_agla is not None:
            del image_tensor_agla
        torch.cuda.empty_cache()
    
    ans_file.close()
    print(f"\n✓ Evaluation complete. Results saved to {answers_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VCD+AGLA Combined Qwen-VL Evaluation")
    
    # Model arguments
    parser.add_argument("--model-path", type=str, required=True, help="Path to Qwen-VL model")
    parser.add_argument("--model-base", type=str, default=None, help="Base model path")
    parser.add_argument("--image-folder", type=str, required=True, help="Path to image folder")
    parser.add_argument("--question-file", type=str, required=True, help="Path to question file")
    parser.add_argument("--answers-file", type=str, required=True, help="Path to save answers")
    
    # Generation arguments
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature for sampling")
    parser.add_argument("--top-p", type=float, default=1.0, help="Top-p sampling")
    parser.add_argument("--top-k", type=int, default=None, help="Top-k sampling")
    
    # VCD arguments
    parser.add_argument("--use-vcd", action='store_true', help="Enable VCD")
    parser.add_argument("--noise-step", type=int, default=500, help="VCD noise step (0-999)")
    parser.add_argument("--cd-alpha", type=float, default=1.0, help="VCD contrast strength")
    parser.add_argument("--cd-beta", type=float, default=0.1, help="VCD plausibility threshold")
    
    # AGLA arguments
    parser.add_argument("--use-agla", action='store_true', help="Enable AGLA")
    parser.add_argument("--agla-alpha", type=float, default=1.0, help="AGLA enhancement strength")
    parser.add_argument("--agla-beta", type=float, default=0.5, help="AGLA plausibility threshold")
    
    # Seed
    parser.add_argument("--seed", type=int, default=55, help="Random seed")
    
    args = parser.parse_args()
    set_seed(args.seed)
    
    eval_model(args)

