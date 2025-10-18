#!/bin/bash

# ==========================================
# VCD+AGLA Combined 完整实验脚本
# ==========================================
# 
# 运行所有 36 组实验:
# - 2 方法 (Baseline, VCD+AGLA Combined)
# - 6 数据集 (COCO-POPE, AOKVQA-POPE, Hallucinogen x4)
# - 3 模型 (LLaVA-1.5, LLaVA-1.6, Qwen-VL)
#
# 使用方法:
#   bash run_all_combined_experiments.sh
# ==========================================

set -e  # 遇到错误时退出

# 激活conda环境
source /root/miniconda3/etc/profile.d/conda.sh
conda activate vcd

cd /root/autodl-tmp/COMBINED

# 添加 Python 路径
export PYTHONPATH="/root/autodl-tmp/VCD/experiments:/root/autodl-tmp/COMBINED:$PYTHONPATH"

# 设置 HF 镜像
export HF_ENDPOINT=https://hf-mirror.com
export CUDA_VISIBLE_DEVICES=0

# ==========================================
# 配置参数
# ==========================================
SEED=55
CD_ALPHA=1.0
CD_BETA=0.1
NOISE_STEP=500
AGLA_ALPHA=1.0
AGLA_BETA=0.5

# 模型路径
LLAVA15_MODEL="/root/autodl-tmp/models/llava-v1.5-7b"
LLAVA16_MODEL="/root/autodl-tmp/models/llava-v1.6-vicuna-7b"
QWENVL_MODEL="/root/autodl-tmp/models/Qwen-VL"

# 数据路径
DATA_DIR="/root/autodl-tmp/VCD/experiments/data"
IMAGE_FOLDER="/root/autodl-tmp/VCD/experiments/data/coco/val2014"

# 输出目录
OUTPUT_DIR="/root/autodl-tmp/COMBINED/combined_results"
mkdir -p "$OUTPUT_DIR"

# 日志文件
LOG_FILE="$OUTPUT_DIR/experiment_log.txt"
echo "实验开始时间: $(date)" | tee "$LOG_FILE"

# ==========================================
# 实验计数器
# ==========================================
TOTAL_EXPERIMENTS=36
CURRENT_EXPERIMENT=0
FAILED_EXPERIMENTS=()

# ==========================================
# 辅助函数
# ==========================================
run_experiment() {
    local model_name=$1
    local model_path=$2
    local dataset_name=$3
    local dataset_file=$4
    local method=$5
    local script=$6
    local conv_mode=${7:-"llava_v1"}
    
    CURRENT_EXPERIMENT=$((CURRENT_EXPERIMENT + 1))
    
    echo ""
    echo "=========================================="
    echo "实验 $CURRENT_EXPERIMENT/$TOTAL_EXPERIMENTS"
    echo "模型: $model_name"
    echo "数据集: $dataset_name"
    echo "方法: $method"
    echo "=========================================="
    
    local output_file="$OUTPUT_DIR/${model_name}_${dataset_name}_${method}_seed${SEED}.jsonl"
    
    # 检查是否已完成
    if [ -f "$output_file" ]; then
        local line_count=$(wc -l < "$output_file")
        if [ "$line_count" -ge 2900 ]; then
            echo "✓ 已完成 (跳过): $output_file ($line_count 行)"
            echo "$(date) - SKIPPED: $model_name $dataset_name $method" | tee -a "$LOG_FILE"
            return 0
        fi
    fi
    
    local start_time=$(date +%s)
    
    # 根据方法构建命令
    if [ "$method" == "baseline" ]; then
        # Baseline: 不使用 VCD 或 AGLA
        if [ "$script" == "llava" ]; then
            python run_pope_combined.py \
                --model-path "$model_path" \
                --image-folder "$IMAGE_FOLDER" \
                --question-file "$dataset_file" \
                --answers-file "$output_file" \
                --conv-mode "$conv_mode" \
                --temperature 1.0 \
                --seed $SEED
        else
            python run_qwenvl_combined.py \
                --model-path "$model_path" \
                --image-folder "$IMAGE_FOLDER" \
                --question-file "$dataset_file" \
                --answers-file "$output_file" \
                --temperature 1.0 \
                --seed $SEED
        fi
    else
        # Combined: 使用 VCD + AGLA
        if [ "$script" == "llava" ]; then
            python run_pope_combined.py \
                --model-path "$model_path" \
                --image-folder "$IMAGE_FOLDER" \
                --question-file "$dataset_file" \
                --answers-file "$output_file" \
                --conv-mode "$conv_mode" \
                --use-vcd --use-agla \
                --cd-alpha $CD_ALPHA --cd-beta $CD_BETA --noise-step $NOISE_STEP \
                --agla-alpha $AGLA_ALPHA --agla-beta $AGLA_BETA \
                --temperature 1.0 \
                --seed $SEED
        else
            python run_qwenvl_combined.py \
                --model-path "$model_path" \
                --image-folder "$IMAGE_FOLDER" \
                --question-file "$dataset_file" \
                --answers-file "$output_file" \
                --use-vcd --use-agla \
                --cd-alpha $CD_ALPHA --cd-beta $CD_BETA --noise-step $NOISE_STEP \
                --agla-alpha $AGLA_ALPHA --agla-beta $AGLA_BETA \
                --temperature 1.0 \
                --seed $SEED
        fi
    fi
    
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "✓ 完成 (耗时: ${duration}秒)"
        echo "$(date) - SUCCESS: $model_name $dataset_name $method (${duration}s)" | tee -a "$LOG_FILE"
    else
        echo "✗ 失败 (退出码: $exit_code)"
        echo "$(date) - FAILED: $model_name $dataset_name $method (exit code: $exit_code)" | tee -a "$LOG_FILE"
        FAILED_EXPERIMENTS+=("$model_name $dataset_name $method")
    fi
    
    return $exit_code
}

# ==========================================
# LLaVA-1.5 实验
# ==========================================
echo ""
echo "=========================================="
echo "开始 LLaVA-1.5 实验"
echo "=========================================="

# COCO POPE (已完成，跳过)
echo "跳过 LLaVA-1.5 COCO POPE (已在之前完成)"

# AOKVQA POPE
run_experiment "llava15" "$LLAVA15_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "baseline" "llava" "llava_v1"
run_experiment "llava15" "$LLAVA15_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "combined" "llava" "llava_v1"

# Hallucinogen - Identification
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "baseline" "llava" "llava_v1"
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "combined" "llava" "llava_v1"

# Hallucinogen - Localization
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "baseline" "llava" "llava_v1"
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "combined" "llava" "llava_v1"

# Hallucinogen - Visual Context
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "baseline" "llava" "llava_v1"
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "combined" "llava" "llava_v1"

# Hallucinogen - Counterfactual
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "baseline" "llava" "llava_v1"
run_experiment "llava15" "$LLAVA15_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "combined" "llava" "llava_v1"

# ==========================================
# LLaVA-1.6 实验
# ==========================================
echo ""
echo "=========================================="
echo "开始 LLaVA-1.6 实验"
echo "=========================================="

# COCO POPE
run_experiment "llava16" "$LLAVA16_MODEL" "coco_pope" \
    "$DATA_DIR/POPE/coco/coco_pope_popular.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "coco_pope" \
    "$DATA_DIR/POPE/coco/coco_pope_popular.json" "combined" "llava" "vicuna_v1"

# AOKVQA POPE
run_experiment "llava16" "$LLAVA16_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "combined" "llava" "vicuna_v1"

# Hallucinogen - Identification
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "combined" "llava" "vicuna_v1"

# Hallucinogen - Localization
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "combined" "llava" "vicuna_v1"

# Hallucinogen - Visual Context
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "combined" "llava" "vicuna_v1"

# Hallucinogen - Counterfactual
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "baseline" "llava" "vicuna_v1"
run_experiment "llava16" "$LLAVA16_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "combined" "llava" "vicuna_v1"

# ==========================================
# Qwen-VL 实验
# ==========================================
echo ""
echo "=========================================="
echo "开始 Qwen-VL 实验"
echo "=========================================="

# COCO POPE
run_experiment "qwenvl" "$QWENVL_MODEL" "coco_pope" \
    "$DATA_DIR/POPE/coco/coco_pope_popular.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "coco_pope" \
    "$DATA_DIR/POPE/coco/coco_pope_popular.json" "combined" "qwenvl"

# AOKVQA POPE
run_experiment "qwenvl" "$QWENVL_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "aokvqa_pope" \
    "$DATA_DIR/POPE/aokvqa/aokvqa_pope_popular.json" "combined" "qwenvl"

# Hallucinogen - Identification
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_identification" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_identification.json" "combined" "qwenvl"

# Hallucinogen - Localization
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_localization" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_localization.json" "combined" "qwenvl"

# Hallucinogen - Visual Context
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_visual_context" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_visual_context.json" "combined" "qwenvl"

# Hallucinogen - Counterfactual
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "baseline" "qwenvl"
run_experiment "qwenvl" "$QWENVL_MODEL" "hallucinogen_counterfactual" \
    "$DATA_DIR/HALLUCINOGEN/hallucinogen_counterfactual.json" "combined" "qwenvl"

# ==========================================
# 总结
# ==========================================
echo ""
echo "=========================================="
echo "所有实验完成"
echo "=========================================="
echo "实验结束时间: $(date)" | tee -a "$LOG_FILE"
echo "总实验数: $TOTAL_EXPERIMENTS"
echo "失败实验数: ${#FAILED_EXPERIMENTS[@]}"

if [ ${#FAILED_EXPERIMENTS[@]} -gt 0 ]; then
    echo ""
    echo "失败的实验:"
    for exp in "${FAILED_EXPERIMENTS[@]}"; do
        echo "  - $exp"
    done
fi

echo ""
echo "结果保存在: $OUTPUT_DIR"
echo "日志文件: $LOG_FILE"

