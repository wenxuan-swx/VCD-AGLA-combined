#!/bin/bash
# VCD + AGLA Combined Method - Parameter Grid Search
#
# This script performs grid search over key parameters to find optimal settings

set -e

# Configuration
MODEL_PATH="/path/to/llava-v1.5-7b"  # UPDATE THIS
IMAGE_FOLDER="/path/to/coco/val2014"  # UPDATE THIS
QUESTION_FILE="/path/to/pope_coco_val.jsonl"  # UPDATE THIS (use validation set)
OUTPUT_DIR="./output/grid_search"

mkdir -p $OUTPUT_DIR

echo "=========================================="
echo "VCD + AGLA Parameter Grid Search"
echo "=========================================="
echo ""

# Parameter grids
CD_ALPHAS=(0.5 1.0 1.5)
CD_BETAS=(0.05 0.1 0.2)
AGLA_ALPHAS=(0.5 1.0 1.5)
NOISE_STEPS=(300 500 700)

# Fixed AGLA beta for simplicity
AGLA_BETA=0.5

total_runs=$((${#CD_ALPHAS[@]} * ${#CD_BETAS[@]} * ${#AGLA_ALPHAS[@]} * ${#NOISE_STEPS[@]}))
current_run=0

echo "Total parameter combinations: $total_runs"
echo ""

# Grid search
for cd_alpha in "${CD_ALPHAS[@]}"; do
    for cd_beta in "${CD_BETAS[@]}"; do
        for agla_alpha in "${AGLA_ALPHAS[@]}"; do
            for noise_step in "${NOISE_STEPS[@]}"; do
                current_run=$((current_run + 1))
                
                # Create output filename
                output_file="$OUTPUT_DIR/cd${cd_alpha}_${cd_beta}_agla${agla_alpha}_noise${noise_step}.jsonl"
                
                echo "[$current_run/$total_runs] Testing: cd_alpha=$cd_alpha, cd_beta=$cd_beta, agla_alpha=$agla_alpha, noise_step=$noise_step"
                
                # Run evaluation
                python run_combined_llava.py \
                    --model-path $MODEL_PATH \
                    --image-folder $IMAGE_FOLDER \
                    --question-file $QUESTION_FILE \
                    --answers-file $output_file \
                    --use-vcd --use-agla \
                    --cd-alpha $cd_alpha \
                    --cd-beta $cd_beta \
                    --agla-alpha $agla_alpha \
                    --agla-beta $AGLA_BETA \
                    --noise-step $noise_step \
                    --temperature 1.0 \
                    --max-new-tokens 512 \
                    2>&1 | tee "$OUTPUT_DIR/log_cd${cd_alpha}_${cd_beta}_agla${agla_alpha}_noise${noise_step}.txt"
                
                echo "  Completed: $output_file"
                echo ""
            done
        done
    done
done

echo "=========================================="
echo "Grid Search Complete!"
echo "=========================================="
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "1. Evaluate all results with POPE evaluation script"
echo "2. Find best parameter combination"
echo "3. Run full evaluation with best parameters"
echo ""

