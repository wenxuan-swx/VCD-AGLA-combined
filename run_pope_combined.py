"""
VCD + AGLA Combined Evaluation Script for POPE Dataset

This script combines VCD and AGLA methods for hallucination reduction.
Based on AGLA's run_llava.py with VCD+AGLA three-way contrastive decoding.

Usage:
    # Baseline
    python run_pope_combined.py --model-path /path/to/llava --question-file pope.json --answers-file output.jsonl

    # VCD only
    python run_pope_combined.py --model-path /path/to/llava --question-file pope.json --answers-file output.jsonl \\
        --use-vcd --cd-alpha 1.0 --cd-beta 0.1 --noise-step 500

    # AGLA only
    python run_pope_combined.py --model-path /path/to/llava --question-file pope.json --answers-file output.jsonl \\
        --use-agla --agla-alpha 1.0 --agla-beta 0.5

    # VCD + AGLA Combined
    python run_pope_combined.py --model-path /path/to/llava --question-file pope.json --answers-file output.jsonl \\
        --use-vcd --use-agla --cd-alpha 1.0 --cd-beta 0.1 --noise-step 500 --agla-alpha 1.0 --agla-beta 0.5
"""

import argparse
import json
from tqdm import tqdm
import sys
import os
import torch
from PIL import Image
from transformers import set_seed

# Add VCD experiments path for LAVIS (must be first for LAVIS compatibility)
sys.path.insert(0, '/root/autodl-tmp/VCD/experiments')
# Add COMBINED directory to path (for our modified llava)
sys.path.insert(0, '/root/autodl-tmp/COMBINED')

# Import LLaVA components
from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria

# Import VCD+AGLA sampling
from sample_vcd_agla import evolve_vcd_agla_sampling

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
    # Evolve sampling to VCD+AGLA
    evolve_vcd_agla_sampling()
    print("✓ Evolved sampling function to VCD+AGLA three-way contrastive decoding")
    
    # Disable torch init
    disable_torch_init()
    
    # Load LLaVA model
    model_path = os.path.expanduser(args.model_path)
    model_name = get_model_name_from_path(model_path)
    print(f"Loading LLaVA model: {model_name} from {model_path}")
    tokenizer, model, image_processor, context_len = load_pretrained_model(
        model_path, args.model_base, model_name
    )
    
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
            "blip_image_text_matching", "large", device=device, is_eval=True
        )
        loader = transforms.Compose([transforms.ToTensor()])
        print("✓ BLIP-ITM loaded")
    
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
        
        # Prepare prompt
        if model.config.mm_use_im_start_end:
            qs = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + question
        else:
            qs = DEFAULT_IMAGE_TOKEN + '\n' + question
        
        conv = conv_templates[args.conv_mode].copy()
        conv.append_message(conv.roles[0], qs + " Please answer this question with one word.")
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()
        
        input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()
        
        # Load image
        try:
            raw_image = Image.open(os.path.join(args.image_folder, image_file)).convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_file}: {e}")
            continue
        
        # Prepare original image tensor
        raw_image_tensor = image_processor.preprocess(raw_image, return_tensors='pt')['pixel_values'][0]
        
        # Prepare VCD noisy image
        image_tensor_vcd = None
        if args.use_vcd:
            image_tensor_vcd = add_diffusion_noise(raw_image_tensor, args.noise_step)
        
        # Prepare AGLA augmented image
        image_tensor_agla = None
        if args.use_agla and model_itm is not None:
            try:
                tensor_image = loader(raw_image.resize((384, 384)))
                image_blip = vis_processors["eval"](raw_image).unsqueeze(0).to('cuda')
                question_blip = text_processors["eval"](question)
                tokenized_text = model_itm.tokenizer(
                    question_blip, padding='longest', truncation=True, return_tensors="pt"
                ).to('cuda')
                
                augmented_image = augmentation(
                    image_blip, question_blip, tensor_image,
                    model_itm, tokenized_text, raw_image
                )
                image_tensor_agla = image_processor.preprocess(
                    augmented_image, return_tensors='pt'
                )['pixel_values'][0]
            except Exception as e:
                print(f"Warning: Failed to generate AGLA image for question {idx}: {e}")
                image_tensor_agla = None
        
        # Generate
        stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
        keywords = [stop_str]
        stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)
        
        with torch.inference_mode():
            output_ids = model.generate(
                input_ids,
                images=raw_image_tensor.unsqueeze(0).half().cuda(),
                images_cd=(image_tensor_vcd.unsqueeze(0).half().cuda() if image_tensor_vcd is not None else None),
                images_agla=(image_tensor_agla.unsqueeze(0).half().cuda() if image_tensor_agla is not None else None),
                cd_alpha=args.cd_alpha,
                cd_beta=args.cd_beta,
                agla_alpha=args.agla_alpha,
                agla_beta=args.agla_beta,
                do_sample=True,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                max_new_tokens=1024,
                use_cache=True
            )
        
        input_token_len = input_ids.shape[1]
        outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
        outputs = outputs.strip()
        if outputs.endswith(stop_str):
            outputs = outputs[:-len(stop_str)]
        outputs = outputs.strip()
        
        # Save answer
        ans_file.write(json.dumps({
            "question_id": idx,
            "prompt": question,
            "text": outputs,
            "model_id": model_name,
            "image": image_file,
            "metadata": {}
        }) + "\n")
        ans_file.flush()
    
    ans_file.close()
    print(f"\n✓ Evaluation complete. Results saved to {answers_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VCD+AGLA Combined POPE Evaluation")
    
    # Model arguments
    parser.add_argument("--model-path", type=str, required=True, help="Path to LLaVA model")
    parser.add_argument("--model-base", type=str, default=None, help="Base model path")
    parser.add_argument("--image-folder", type=str, required=True, help="Path to image folder")
    parser.add_argument("--question-file", type=str, required=True, help="Path to question file")
    parser.add_argument("--answers-file", type=str, required=True, help="Path to save answers")
    parser.add_argument("--conv-mode", type=str, default="llava_v1", help="Conversation mode")
    
    # Generation arguments
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature for sampling")
    parser.add_argument("--top-p", type=float, default=None, help="Top-p sampling")
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

