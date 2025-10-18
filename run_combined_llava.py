"""
VCD + AGLA Combined Evaluation Script for LLaVA

This script evaluates the combined VCD+AGLA method on:
- POPE dataset (COCO, A-OKVQA)
- Hallucinogen dataset

Usage:
    # VCD only
    python run_combined_llava.py --model-path /path/to/llava \
        --question-file pope_coco.jsonl --answers-file output.jsonl \
        --use-vcd --cd-alpha 1.0 --cd-beta 0.1

    # AGLA only
    python run_combined_llava.py --model-path /path/to/llava \
        --question-file pope_coco.jsonl --answers-file output.jsonl \
        --use-agla --agla-alpha 1.0 --agla-beta 0.5

    # Combined VCD + AGLA
    python run_combined_llava.py --model-path /path/to/llava \
        --question-file pope_coco.jsonl --answers-file output.jsonl \
        --use-vcd --use-agla \
        --cd-alpha 1.0 --cd-beta 0.1 \
        --agla-alpha 1.0 --agla-beta 0.5
"""

import argparse
import json
import os
from tqdm import tqdm
import torch
from PIL import Image
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import combined sampling
from sample_vcd_agla import evolve_vcd_agla_sampling

# Import utilities
from utils.vcd_add_noise import add_diffusion_noise

# Try to import AGLA augmentation (requires LAVIS)
try:
    from utils.augmentation import augmentation
    AGLA_AVAILABLE = True
except (ImportError, KeyError, ModuleNotFoundError) as e:
    AGLA_AVAILABLE = False
    augmentation = None
    import warnings
    warnings.warn(f"AGLA augmentation not available: {e}. Use --use-vcd only or install LAVIS.")

# Import LLaVA components
try:
    from llava.model.builder import load_pretrained_model
    from llava.mm_utils import tokenizer_image_token, KeywordsStoppingCriteria
    from llava.constants import IMAGE_TOKEN_INDEX
    from llava.conversation import conv_templates, SeparatorStyle
except ImportError:
    print("Error: Could not import llava modules. Please ensure llava is installed.")
    print("You may need to add the AGLA or VCD llava directory to your Python path.")
    sys.exit(1)

# Import BLIP-ITM for AGLA
try:
    from lavis.models import load_model_and_preprocess
    from torchvision import transforms
except ImportError:
    print("Warning: Could not import lavis. AGLA functionality will not be available.")
    print("Install with: pip install salesforce-lavis")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="VCD+AGLA Combined Evaluation")
    
    # Model arguments
    parser.add_argument("--model-path", type=str, required=True, help="Path to LLaVA model")
    parser.add_argument("--model-base", type=str, default=None, help="Base model path")
    parser.add_argument("--model-name", type=str, default="llava-v1.5-7b", help="Model name")
    
    # Data arguments
    parser.add_argument("--image-folder", type=str, required=True, help="Path to image folder")
    parser.add_argument("--question-file", type=str, required=True, help="Path to question file (JSONL)")
    parser.add_argument("--answers-file", type=str, required=True, help="Path to save answers (JSONL)")
    
    # Generation arguments
    parser.add_argument("--conv-mode", type=str, default="llava_v1", help="Conversation mode")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature")
    parser.add_argument("--max-new-tokens", type=int, default=1024, help="Maximum new tokens")
    
    # VCD arguments
    parser.add_argument("--use-vcd", action='store_true', help="Enable VCD")
    parser.add_argument("--noise-step", type=int, default=500, help="VCD noise step (0-999)")
    parser.add_argument("--cd-alpha", type=float, default=1.0, help="VCD contrast strength")
    parser.add_argument("--cd-beta", type=float, default=0.1, help="VCD plausibility threshold")
    
    # AGLA arguments
    parser.add_argument("--use-agla", action='store_true', help="Enable AGLA")
    parser.add_argument("--agla-alpha", type=float, default=1.0, help="AGLA enhancement strength")
    parser.add_argument("--agla-beta", type=float, default=0.5, help="AGLA plausibility threshold")
    
    # Other arguments
    parser.add_argument("--num-gpus", type=int, default=1, help="Number of GPUs")
    parser.add_argument("--debug", action='store_true', help="Enable debug logging")
    
    return parser.parse_args()


def load_models(args):
    """Load LLaVA and BLIP-ITM models"""
    logger.info(f"Loading LLaVA model from {args.model_path}")
    
    # Load LLaVA
    tokenizer, model, image_processor, context_len = load_pretrained_model(
        args.model_path, args.model_base, args.model_name
    )
    
    # Load BLIP-ITM if AGLA is enabled
    model_itm = None
    vis_processors = None
    text_processors = None

    if args.use_agla:
        if not AGLA_AVAILABLE:
            logger.error("AGLA requested but not available. Please install LAVIS:")
            logger.error("  pip install salesforce-lavis")
            sys.exit(1)

        try:
            logger.info("Loading BLIP-ITM model for AGLA")
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            model_itm, vis_processors, text_processors = load_model_and_preprocess(
                "blip_image_text_matching", "large", device=device, is_eval=True
            )
        except Exception as e:
            logger.error(f"Failed to load BLIP-ITM: {e}")
            logger.error("AGLA will be disabled")
            args.use_agla = False
    
    return tokenizer, model, image_processor, context_len, model_itm, vis_processors, text_processors


def prepare_images(raw_image, question, image_processor, args, model_itm, vis_processors, text_processors):
    """
    Prepare three types of images:
    1. Original image
    2. VCD noisy image (if use_vcd)
    3. AGLA augmented image (if use_agla)
    """
    # Original image
    image_tensor = image_processor.preprocess(raw_image, return_tensors='pt')['pixel_values'][0]
    
    # VCD noisy image
    image_tensor_vcd = None
    if args.use_vcd:
        image_tensor_vcd = add_diffusion_noise(image_tensor, args.noise_step)
        logger.debug(f"Added VCD noise at step {args.noise_step}")
    
    # AGLA augmented image
    image_tensor_agla = None
    if args.use_agla and model_itm is not None:
        try:
            # Prepare image for BLIP
            loader = transforms.Compose([transforms.ToTensor()])
            tensor_image = loader(raw_image.resize((384, 384)))
            image_blip = vis_processors["eval"](raw_image).unsqueeze(0).to('cuda')
            
            # Prepare text for BLIP
            question_blip = text_processors["eval"](question)
            tokenized_text = model_itm.tokenizer(
                question_blip, padding='longest', truncation=True, return_tensors="pt"
            ).to('cuda')
            
            # Generate augmented image
            augmented_image = augmentation(
                image_blip, question_blip, tensor_image, 
                model_itm, tokenized_text, raw_image
            )
            
            # Preprocess augmented image
            image_tensor_agla = image_processor.preprocess(
                augmented_image, return_tensors='pt'
            )['pixel_values'][0]
            
            logger.debug("Generated AGLA augmented image")
        except Exception as e:
            logger.error(f"Error generating AGLA image: {e}")
            image_tensor_agla = None
    
    return image_tensor, image_tensor_vcd, image_tensor_agla


def evaluate(args):
    """Main evaluation function"""
    # Evolve sampling function
    evolve_vcd_agla_sampling()
    logger.info("Evolved sampling function to VCD+AGLA")
    
    # Load models
    tokenizer, model, image_processor, context_len, model_itm, vis_processors, text_processors = load_models(args)
    
    # Load questions
    logger.info(f"Loading questions from {args.question_file}")
    questions = [json.loads(q) for q in open(args.question_file, "r")]
    
    # Open answers file
    os.makedirs(os.path.dirname(args.answers_file) if os.path.dirname(args.answers_file) else '.', exist_ok=True)
    ans_file = open(args.answers_file, "w")
    
    logger.info(f"Starting evaluation on {len(questions)} questions")
    logger.info(f"VCD: {args.use_vcd}, AGLA: {args.use_agla}")
    
    # Process each question
    for i, line in enumerate(tqdm(questions, desc="Evaluating")):
        idx = line.get("question_id", i)
        image_file = line["image"]
        question = line["text"]
        
        # Prepare prompt
        qs = f"<image>\n{question}"
        conv = conv_templates[args.conv_mode].copy()
        conv.append_message(conv.roles[0], qs + " Please answer this question with one word.")
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()
        
        # Tokenize
        input_ids = tokenizer_image_token(
            prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt'
        ).unsqueeze(0).cuda()
        
        # Load and prepare images
        try:
            image_path = os.path.join(args.image_folder, image_file)
            raw_image = Image.open(image_path).convert('RGB')
        except Exception as e:
            logger.error(f"Error loading image {image_file}: {e}")
            continue
        
        image_tensor, image_tensor_vcd, image_tensor_agla = prepare_images(
            raw_image, question, image_processor, args, 
            model_itm, vis_processors, text_processors
        )
        
        # Generate
        try:
            with torch.inference_mode():
                output_ids = model.generate(
                    input_ids,
                    images=image_tensor.unsqueeze(0).half().cuda(),
                    images_cd=(image_tensor_vcd.unsqueeze(0).half().cuda() 
                              if image_tensor_vcd is not None else None),
                    images_agla=(image_tensor_agla.unsqueeze(0).half().cuda() 
                                if image_tensor_agla is not None else None),
                    cd_alpha=args.cd_alpha,
                    cd_beta=args.cd_beta,
                    agla_alpha=args.agla_alpha,
                    agla_beta=args.agla_beta,
                    do_sample=True,
                    temperature=args.temperature,
                    max_new_tokens=args.max_new_tokens,
                    use_cache=True
                )
            
            # Decode output
            outputs = tokenizer.batch_decode(
                output_ids[:, input_ids.shape[1]:], skip_special_tokens=True
            )[0].strip()
            
        except Exception as e:
            logger.error(f"Error generating for question {idx}: {e}")
            outputs = "error"
        
        # Save result
        ans_file.write(json.dumps({
            "question_id": idx,
            "text": outputs,
            "image": image_file
        }) + "\n")
        ans_file.flush()
        
        if args.debug and i < 5:
            logger.debug(f"Q: {question}")
            logger.debug(f"A: {outputs}")
    
    ans_file.close()
    logger.info(f"Evaluation complete. Results saved to {args.answers_file}")


if __name__ == "__main__":
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    evaluate(args)

