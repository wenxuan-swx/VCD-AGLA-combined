#!/bin/bash
# VCD + AGLA Combined Method - POPE Evaluation Script
#
# This script runs evaluation on POPE dataset (COCO and A-OKVQA)
# with different method combinations

set -e  # Exit on error

# Configuration
MODEL_PATH="/path/to/llava-v1.5-7b"  # UPDATE THIS
COCO_IMAGE_FOLDER="/path/to/coco/val2014"  # UPDATE THIS
POPE_COCO_FILE="/path/to/pope_coco.jsonl"  # UPDATE THIS
OUTPUT_DIR="./output/pope"

# Create output directory
mkdir -p $OUTPUT_DIR

echo "=========================================="
echo "VCD + AGLA POPE Evaluation"
echo "=========================================="
echo "Model: $MODEL_PATH"
echo "Output: $OUTPUT_DIR"
echo ""

# 1. Baseline (no VCD, no AGLA)
echo "[1/4] Running Baseline..."
python run_combined_llava.py \
    --model-path $MODEL_PATH \
    --image-folder $COCO_IMAGE_FOLDER \
    --question-file $POPE_COCO_FILE \
    --answers-file $OUTPUT_DIR/baseline.jsonl \
    --temperature 1.0 \
    --max-new-tokens 1024

# 2. VCD only
echo "[2/4] Running VCD only..."
python run_combined_llava.py \
    --model-path $MODEL_PATH \
    --image-folder $COCO_IMAGE_FOLDER \
    --question-file $POPE_COCO_FILE \
    --answers-file $OUTPUT_DIR/vcd_only.jsonl \
    --use-vcd \
    --cd-alpha 1.0 \
    --cd-beta 0.1 \
    --noise-step 500 \
    --temperature 1.0 \
    --max-new-tokens 1024

# 3. AGLA only
echo "[3/4] Running AGLA only..."
python run_combined_llava.py \
    --model-path $MODEL_PATH \
    --image-folder $COCO_IMAGE_FOLDER \
    --question-file $POPE_COCO_FILE \
    --answers-file $OUTPUT_DIR/agla_only.jsonl \
    --use-agla \
    --agla-alpha 1.0 \
    --agla-beta 0.5 \
    --temperature 1.0 \
    --max-new-tokens 1024

# 4. Combined VCD + AGLA
echo "[4/4] Running VCD + AGLA Combined..."
python run_combined_llava.py \
    --model-path $MODEL_PATH \
    --image-folder $COCO_IMAGE_FOLDER \
    --question-file $POPE_COCO_FILE \
    --answers-file $OUTPUT_DIR/combined.jsonl \
    --use-vcd --use-agla \
    --cd-alpha 1.0 \
    --cd-beta 0.1 \
    --agla-alpha 1.0 \
    --agla-beta 0.5 \
    --noise-step 500 \
    --temperature 1.0 \
    --max-new-tokens 1024

echo ""
echo "=========================================="
echo "Evaluation Complete!"
echo "=========================================="
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "1. Evaluate results with POPE evaluation script"
echo "2. Compare F1 scores across methods"
echo "3. Analyze error cases"
echo ""

