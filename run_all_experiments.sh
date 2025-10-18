#!/bin/bash

# VCD + AGLA 组合方法 - POPE 完整评估实验
# 自动运行 4 个对比实验并生成评估报告

set -e  # Exit on error

# ============================================================
# 配置参数
# ============================================================

MODEL_PATH="/root/autodl-tmp/models/llava-v1.5-7b"
IMAGE_FOLDER="/root/autodl-tmp/VCD_data/coco/val2014"
QUESTION_FILE="/root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json"
RESULTS_DIR="pope_results"
TEMPERATURE=1.0

# VCD 参数
CD_ALPHA=1.0
CD_BETA=0.1
NOISE_STEP=500

# AGLA 参数
AGLA_ALPHA=1.0
AGLA_BETA=0.5

# ============================================================
# 准备工作
# ============================================================

echo "============================================================"
echo "VCD + AGLA 组合方法 - POPE 完整评估实验"
echo "============================================================"
echo ""
echo "模型: LLaVA-1.5-7B"
echo "数据集: COCO POPE Popular (3000 questions)"
echo "结果目录: $RESULTS_DIR"
echo ""

# 创建结果目录
mkdir -p "$RESULTS_DIR"

# 检查 GPU
echo "检查 GPU 状态..."
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
echo ""

# 记录开始时间
START_TIME=$(date +%s)
echo "开始时间: $(date)"
echo ""

# ============================================================
# 实验 1: Baseline
# ============================================================

echo "============================================================"
echo "实验 1/4: Baseline (标准解码)"
echo "============================================================"
echo ""

EXP1_START=$(date +%s)

python run_pope_combined.py \
  --model-path "$MODEL_PATH" \
  --image-folder "$IMAGE_FOLDER" \
  --question-file "$QUESTION_FILE" \
  --answers-file "$RESULTS_DIR/baseline.jsonl" \
  --temperature "$TEMPERATURE"

EXP1_END=$(date +%s)
EXP1_TIME=$((EXP1_END - EXP1_START))

echo ""
echo "✓ 实验 1 完成 (用时: ${EXP1_TIME}s)"
echo ""

# 评估结果
python eval_pope.py \
  --gt_file "$QUESTION_FILE" \
  --gen_file "$RESULTS_DIR/baseline.jsonl" \
  --output "$RESULTS_DIR/baseline_metrics.json"

echo ""

# ============================================================
# 实验 2: VCD Only
# ============================================================

echo "============================================================"
echo "实验 2/4: VCD Only"
echo "============================================================"
echo ""
echo "参数: cd_alpha=$CD_ALPHA, cd_beta=$CD_BETA, noise_step=$NOISE_STEP"
echo ""

EXP2_START=$(date +%s)

python run_pope_combined.py \
  --model-path "$MODEL_PATH" \
  --image-folder "$IMAGE_FOLDER" \
  --question-file "$QUESTION_FILE" \
  --answers-file "$RESULTS_DIR/vcd_only.jsonl" \
  --use-vcd \
  --cd-alpha "$CD_ALPHA" \
  --cd-beta "$CD_BETA" \
  --noise-step "$NOISE_STEP" \
  --temperature "$TEMPERATURE"

EXP2_END=$(date +%s)
EXP2_TIME=$((EXP2_END - EXP2_START))

echo ""
echo "✓ 实验 2 完成 (用时: ${EXP2_TIME}s)"
echo ""

# 评估结果
python eval_pope.py \
  --gt_file "$QUESTION_FILE" \
  --gen_file "$RESULTS_DIR/vcd_only.jsonl" \
  --output "$RESULTS_DIR/vcd_only_metrics.json"

echo ""

# ============================================================
# 实验 3: AGLA Only
# ============================================================

echo "============================================================"
echo "实验 3/4: AGLA Only"
echo "============================================================"
echo ""
echo "参数: agla_alpha=$AGLA_ALPHA, agla_beta=$AGLA_BETA"
echo ""

# 检查 LAVIS 是否可用
if python -c "import lavis" 2>/dev/null; then
    echo "✓ LAVIS 已安装"
    echo ""
    
    EXP3_START=$(date +%s)
    
    python run_pope_combined.py \
      --model-path "$MODEL_PATH" \
      --image-folder "$IMAGE_FOLDER" \
      --question-file "$QUESTION_FILE" \
      --answers-file "$RESULTS_DIR/agla_only.jsonl" \
      --use-agla \
      --agla-alpha "$AGLA_ALPHA" \
      --agla-beta "$AGLA_BETA" \
      --temperature "$TEMPERATURE"
    
    EXP3_END=$(date +%s)
    EXP3_TIME=$((EXP3_END - EXP3_START))
    
    echo ""
    echo "✓ 实验 3 完成 (用时: ${EXP3_TIME}s)"
    echo ""
    
    # 评估结果
    python eval_pope.py \
      --gt_file "$QUESTION_FILE" \
      --gen_file "$RESULTS_DIR/agla_only.jsonl" \
      --output "$RESULTS_DIR/agla_only_metrics.json"
    
    echo ""
else
    echo "⚠️  LAVIS 未安装，跳过 AGLA Only 实验"
    echo "   安装命令: pip install salesforce-lavis"
    echo ""
    EXP3_TIME=0
fi

# ============================================================
# 实验 4: VCD + AGLA Combined
# ============================================================

echo "============================================================"
echo "实验 4/4: VCD + AGLA Combined"
echo "============================================================"
echo ""
echo "参数:"
echo "  VCD: cd_alpha=$CD_ALPHA, cd_beta=$CD_BETA, noise_step=$NOISE_STEP"
echo "  AGLA: agla_alpha=$AGLA_ALPHA, agla_beta=$AGLA_BETA"
echo ""

# 检查 LAVIS 是否可用
if python -c "import lavis" 2>/dev/null; then
    EXP4_START=$(date +%s)
    
    python run_pope_combined.py \
      --model-path "$MODEL_PATH" \
      --image-folder "$IMAGE_FOLDER" \
      --question-file "$QUESTION_FILE" \
      --answers-file "$RESULTS_DIR/combined.jsonl" \
      --use-vcd \
      --use-agla \
      --cd-alpha "$CD_ALPHA" \
      --cd-beta "$CD_BETA" \
      --noise-step "$NOISE_STEP" \
      --agla-alpha "$AGLA_ALPHA" \
      --agla-beta "$AGLA_BETA" \
      --temperature "$TEMPERATURE"
    
    EXP4_END=$(date +%s)
    EXP4_TIME=$((EXP4_END - EXP4_START))
    
    echo ""
    echo "✓ 实验 4 完成 (用时: ${EXP4_TIME}s)"
    echo ""
    
    # 评估结果
    python eval_pope.py \
      --gt_file "$QUESTION_FILE" \
      --gen_file "$RESULTS_DIR/combined.jsonl" \
      --output "$RESULTS_DIR/combined_metrics.json"
    
    echo ""
else
    echo "⚠️  LAVIS 未安装，跳过 Combined 实验"
    echo "   安装命令: pip install salesforce-lavis"
    echo ""
    EXP4_TIME=0
fi

# ============================================================
# 生成对比报告
# ============================================================

echo "============================================================"
echo "生成对比报告"
echo "============================================================"
echo ""

python - <<'EOF'
import json
import os
import sys

results_dir = "pope_results"
experiments = [
    ("baseline", "Baseline"),
    ("vcd_only", "VCD Only"),
    ("agla_only", "AGLA Only"),
    ("combined", "VCD + AGLA Combined")
]

print("=" * 90)
print("POPE Evaluation - Comparison Report")
print("=" * 90)
print()
print("Model: LLaVA-1.5-7B")
print("Dataset: COCO POPE Popular (3000 questions)")
print()
print("=" * 90)
print(f"{'Method':<30} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<15}")
print("=" * 90)

baseline_f1 = None
all_results = {}

for exp_name, exp_label in experiments:
    metrics_file = os.path.join(results_dir, f"{exp_name}_metrics.json")
    if os.path.exists(metrics_file):
        with open(metrics_file) as f:
            results = json.load(f)
        
        acc = results['accuracy']
        prec = results['precision']
        rec = results['recall']
        f1 = results['f1']
        
        all_results[exp_name] = results
        
        if exp_name == "baseline":
            baseline_f1 = f1
        
        improvement = ""
        if baseline_f1 is not None and exp_name != "baseline":
            delta = (f1 - baseline_f1) * 100
            improvement = f" (+{delta:.2f}%)" if delta > 0 else f" ({delta:.2f}%)"
        
        print(f"{exp_label:<30} {acc:>6.2%}      {prec:>6.2%}      {rec:>6.2%}      {f1:>6.2%}{improvement}")
    else:
        print(f"{exp_label:<30} {'N/A':<12} {'N/A':<12} {'N/A':<12} {'N/A':<12}")

print("=" * 90)
print()

# 保存汇总结果
summary_file = os.path.join(results_dir, "summary.json")
with open(summary_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"✓ 汇总结果已保存到: {summary_file}")
print()
EOF

# ============================================================
# 总结
# ============================================================

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo "============================================================"
echo "实验完成总结"
echo "============================================================"
echo ""
echo "结束时间: $(date)"
echo "总用时: ${TOTAL_TIME}s ($(($TOTAL_TIME / 60))分钟)"
echo ""
echo "各实验用时:"
echo "  实验 1 (Baseline):  ${EXP1_TIME}s"
echo "  实验 2 (VCD Only):  ${EXP2_TIME}s"
echo "  实验 3 (AGLA Only): ${EXP3_TIME}s"
echo "  实验 4 (Combined):  ${EXP4_TIME}s"
echo ""
echo "结果文件位置: $RESULTS_DIR/"
echo ""
echo "✓ 所有实验完成！"
echo "============================================================"

