#!/bin/bash

# Quick test script to validate the pipeline

set -e

MODEL_PATH="/root/autodl-tmp/models/llava-v1.5-7b"
IMAGE_FOLDER="/root/autodl-tmp/VCD_data/coco/val2014"
QUESTION_FILE="/root/autodl-tmp/COMBINED/pope_test_subset.json"
GT_FILE="/root/autodl-tmp/COMBINED/pope_test_subset.json"
OUTPUT_DIR="/root/autodl-tmp/COMBINED/test_results"

mkdir -p $OUTPUT_DIR

echo "============================================================"
echo "Quick Test - Baseline (20 samples)"
echo "============================================================"
echo ""

# Test baseline
python run_pope_combined.py \
    --model-path "$MODEL_PATH" \
    --image-folder "$IMAGE_FOLDER" \
    --question-file "$QUESTION_FILE" \
    --answers-file "${OUTPUT_DIR}/test_baseline.jsonl" \
    --temperature 1.0

echo ""
echo "✓ Baseline test completed"
echo ""

# Evaluate
python eval_pope.py \
    --gt_file "$GT_FILE" \
    --gen_file "${OUTPUT_DIR}/test_baseline.jsonl"

echo ""
echo "✅ Quick test passed!"

