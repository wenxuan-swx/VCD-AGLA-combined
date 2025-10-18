#!/bin/bash

# VCD + AGLA Combined Method - Full POPE Evaluation Script
# This script runs 4 experiments on COCO POPE dataset:
# 1. Baseline (no VCD, no AGLA)
# 2. VCD only
# 3. AGLA only
# 4. VCD + AGLA Combined

set -e  # Exit on error

# ============================================================
# Configuration
# ============================================================

# Model and data paths
MODEL_PATH="/root/autodl-tmp/models/llava-v1.5-7b"
IMAGE_FOLDER="/root/autodl-tmp/VCD_data/coco/val2014"
QUESTION_FILE="/root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json"
GT_FILE="/root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json"

# Output directory
OUTPUT_DIR="/root/autodl-tmp/COMBINED/pope_results"
mkdir -p $OUTPUT_DIR

# Parameters
SEED=55
TEMPERATURE=1.0
MAX_NEW_TOKENS=1024

# VCD parameters
CD_ALPHA=1.0
CD_BETA=0.1
NOISE_STEP=500

# AGLA parameters
AGLA_ALPHA=1.0
AGLA_BETA=0.5

# ============================================================
# Helper Functions
# ============================================================

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo ""
}

run_evaluation() {
    local exp_name=$1
    local output_file="${OUTPUT_DIR}/${exp_name}.jsonl"
    local result_file="${OUTPUT_DIR}/${exp_name}_results.json"
    local log_file="${OUTPUT_DIR}/${exp_name}.log"
    
    print_header "Running: $exp_name"
    
    # Run inference
    echo "Output: $output_file"
    echo "Log: $log_file"
    echo ""
    
    shift  # Remove first argument (exp_name)
    python run_combined_llava.py \
        --model-path "$MODEL_PATH" \
        --image-folder "$IMAGE_FOLDER" \
        --question-file "$QUESTION_FILE" \
        --answers-file "$output_file" \
        --temperature $TEMPERATURE \
        --max-new-tokens $MAX_NEW_TOKENS \
        --seed $SEED \
        "$@" \
        2>&1 | tee "$log_file"
    
    # Evaluate results
    print_header "Evaluating: $exp_name"
    python eval_pope.py \
        --gt_file "$GT_FILE" \
        --gen_file "$output_file" \
        --output "$result_file"
    
    echo ""
    echo "✓ $exp_name completed"
    echo "  Output: $output_file"
    echo "  Results: $result_file"
    echo ""
}

# ============================================================
# Check Environment
# ============================================================

print_header "Environment Check"

# Check if model exists
if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ Error: Model not found at $MODEL_PATH"
    exit 1
fi
echo "✓ Model found: $MODEL_PATH"

# Check if images exist
if [ ! -d "$IMAGE_FOLDER" ]; then
    echo "❌ Error: Images not found at $IMAGE_FOLDER"
    exit 1
fi
echo "✓ Images found: $IMAGE_FOLDER"

# Check if question file exists
if [ ! -f "$QUESTION_FILE" ]; then
    echo "❌ Error: Question file not found at $QUESTION_FILE"
    exit 1
fi
echo "✓ Question file found: $QUESTION_FILE"

# Check if llava module exists
if [ ! -d "llava" ]; then
    echo "❌ Error: llava module not found in current directory"
    echo "   Please run: cp -r /root/autodl-tmp/AGLA/llava ."
    exit 1
fi
echo "✓ llava module found"

# Check GPU
if ! nvidia-smi &> /dev/null; then
    echo "⚠️  Warning: nvidia-smi not found. GPU may not be available."
else
    echo "✓ GPU available"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
fi

echo ""
read -p "Press Enter to start experiments (or Ctrl+C to cancel)..."

# ============================================================
# Experiment 1: Baseline
# ============================================================

run_evaluation "baseline" \
    # No additional flags

# ============================================================
# Experiment 2: VCD Only
# ============================================================

run_evaluation "vcd_only" \
    --use-vcd \
    --cd-alpha $CD_ALPHA \
    --cd-beta $CD_BETA \
    --noise-step $NOISE_STEP

# ============================================================
# Experiment 3: AGLA Only
# ============================================================

run_evaluation "agla_only" \
    --use-agla \
    --agla-alpha $AGLA_ALPHA \
    --agla-beta $AGLA_BETA

# ============================================================
# Experiment 4: VCD + AGLA Combined
# ============================================================

run_evaluation "combined" \
    --use-vcd \
    --use-agla \
    --cd-alpha $CD_ALPHA \
    --cd-beta $CD_BETA \
    --noise-step $NOISE_STEP \
    --agla-alpha $AGLA_ALPHA \
    --agla-beta $AGLA_BETA

# ============================================================
# Generate Comparison Report
# ============================================================

print_header "Generating Comparison Report"

python - <<EOF
import json
import os

output_dir = "$OUTPUT_DIR"

experiments = [
    ("baseline", "Baseline"),
    ("vcd_only", "VCD Only"),
    ("agla_only", "AGLA Only"),
    ("combined", "VCD + AGLA Combined")
]

print("=" * 80)
print("POPE Evaluation - Comparison Report")
print("=" * 80)
print()
print("Model: LLaVA-1.5-7B")
print("Dataset: COCO POPE Popular (3000 questions)")
print("Parameters:")
print(f"  VCD: alpha={$CD_ALPHA}, beta={$CD_BETA}, noise_step={$NOISE_STEP}")
print(f"  AGLA: alpha={$AGLA_ALPHA}, beta={$AGLA_BETA}")
print()
print("=" * 80)
print(f"{'Method':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
print("=" * 80)

baseline_f1 = None
for exp_name, exp_label in experiments:
    result_file = os.path.join(output_dir, f"{exp_name}_results.json")
    if os.path.exists(result_file):
        with open(result_file) as f:
            results = json.load(f)
        
        acc = results['accuracy']
        prec = results['precision']
        rec = results['recall']
        f1 = results['f1']
        
        if exp_name == "baseline":
            baseline_f1 = f1
        
        improvement = ""
        if baseline_f1 is not None and exp_name != "baseline":
            delta = (f1 - baseline_f1) * 100
            improvement = f" (+{delta:.2f}%)" if delta > 0 else f" ({delta:.2f}%)"
        
        print(f"{exp_label:<25} {acc:>6.2%}      {prec:>6.2%}      {rec:>6.2%}      {f1:>6.2%}{improvement}")
    else:
        print(f"{exp_label:<25} {'N/A':<12} {'N/A':<12} {'N/A':<12} {'N/A':<12}")

print("=" * 80)
print()
print("Results saved to: $OUTPUT_DIR")
print()
EOF

print_header "All Experiments Completed!"

echo "Results directory: $OUTPUT_DIR"
echo ""
echo "Files generated:"
ls -lh $OUTPUT_DIR
echo ""
echo "✅ Full POPE evaluation completed successfully!"

