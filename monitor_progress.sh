#!/bin/bash

# 监控实验进度脚本

RESULTS_DIR="/root/autodl-tmp/COMBINED/combined_results"
LOG_FILE="$RESULTS_DIR/experiment_run.log"

echo "=========================================="
echo "实验进度监控"
echo "=========================================="
echo ""

# 检查日志文件是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "错误：日志文件不存在"
    exit 1
fi

# 显示开始时间
echo "开始时间："
grep "实验开始时间" "$LOG_FILE"
echo ""

# 显示当前实验
echo "当前实验："
tail -100 "$LOG_FILE" | grep -E "实验 [0-9]+/36" | tail -1
tail -100 "$LOG_FILE" | grep -E "模型:|数据集:|方法:" | tail -3
echo ""

# 显示最新进度
echo "最新进度："
tail -5 "$LOG_FILE" | grep "Evaluating:" | tail -1
echo ""

# 统计已完成的结果文件
echo "已完成的实验结果："
ls -lh "$RESULTS_DIR"/*.jsonl 2>/dev/null | wc -l
echo ""

# 显示结果文件列表
echo "结果文件列表："
ls -lh "$RESULTS_DIR"/*.jsonl 2>/dev/null | awk '{print $9, $5}'
echo ""

# 检查是否有错误
echo "错误检查："
if grep -q "Error\|错误\|Failed" "$LOG_FILE"; then
    echo "⚠️  发现错误，最近的错误信息："
    grep -i "error\|错误\|failed" "$LOG_FILE" | tail -5
else
    echo "✓ 未发现错误"
fi
echo ""

# 估算剩余时间
COMPLETED=$(ls -1 "$RESULTS_DIR"/*.jsonl 2>/dev/null | wc -l)
TOTAL=36
REMAINING=$((TOTAL - COMPLETED))

if [ $COMPLETED -gt 0 ]; then
    START_TIME=$(grep "实验开始时间" "$LOG_FILE" | awk '{print $3, $4, $5, $6, $7}')
    START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || echo "0")
    CURRENT_EPOCH=$(date +%s)
    
    if [ "$START_EPOCH" != "0" ]; then
        ELAPSED=$((CURRENT_EPOCH - START_EPOCH))
        AVG_TIME=$((ELAPSED / COMPLETED))
        REMAINING_TIME=$((AVG_TIME * REMAINING))
        
        echo "时间估算："
        echo "  已完成: $COMPLETED/$TOTAL 个实验"
        echo "  已用时间: $((ELAPSED / 60)) 分钟"
        echo "  平均每个实验: $((AVG_TIME / 60)) 分钟"
        echo "  预计剩余时间: $((REMAINING_TIME / 60)) 分钟"
        echo "  预计完成时间: $(date -d "+${REMAINING_TIME} seconds" "+%Y-%m-%d %H:%M:%S")"
    fi
fi

echo ""
echo "=========================================="

