#!/bin/bash

# 持续监控实验进度脚本
# 每30秒更新一次进度

RESULTS_DIR="/root/autodl-tmp/COMBINED/combined_results"
LOG_FILE="$RESULTS_DIR/experiment_run.log"
MONITOR_LOG="$RESULTS_DIR/monitor_log.txt"

echo "=========================================="
echo "开始持续监控实验进度"
echo "监控时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 初始化监控日志
echo "监控开始时间: $(date '+%Y-%m-%d %H:%M:%S')" > "$MONITOR_LOG"

TOTAL_EXPERIMENTS=36
LAST_COMPLETED=0

while true; do
    clear
    echo "=========================================="
    echo "实验进度监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""
    
    # 检查日志文件是否存在
    if [ ! -f "$LOG_FILE" ]; then
        echo "⚠️  日志文件不存在，等待实验启动..."
        sleep 30
        continue
    fi
    
    # 统计已完成的实验
    COMPLETED=$(ls -1 "$RESULTS_DIR"/*.jsonl 2>/dev/null | grep -v "test_" | wc -l)
    REMAINING=$((TOTAL_EXPERIMENTS - COMPLETED))
    PROGRESS=$((COMPLETED * 100 / TOTAL_EXPERIMENTS))
    
    echo "📊 总体进度"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  已完成: $COMPLETED / $TOTAL_EXPERIMENTS 个实验 ($PROGRESS%)"
    echo "  剩余: $REMAINING 个实验"
    echo ""
    
    # 显示进度条
    BAR_LENGTH=40
    FILLED=$((PROGRESS * BAR_LENGTH / 100))
    EMPTY=$((BAR_LENGTH - FILLED))
    printf "  ["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%${EMPTY}s" | tr ' ' '░'
    printf "] $PROGRESS%%\n"
    echo ""
    
    # 显示当前运行的实验
    echo "🔄 当前实验"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    CURRENT_EXP=$(tail -200 "$LOG_FILE" | grep -E "实验 [0-9]+/36" | tail -1)
    if [ -n "$CURRENT_EXP" ]; then
        echo "  $CURRENT_EXP"
        tail -200 "$LOG_FILE" | grep -E "模型:|数据集:|方法:" | tail -3 | sed 's/^/  /'
    else
        echo "  等待实验信息..."
    fi
    echo ""
    
    # 显示最新进度
    echo "📈 最新进度"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    LATEST_PROGRESS=$(tail -10 "$LOG_FILE" | grep "Evaluating:" | tail -1)
    if [ -n "$LATEST_PROGRESS" ]; then
        echo "  $LATEST_PROGRESS"
    else
        echo "  等待进度信息..."
    fi
    echo ""
    
    # 时间估算
    START_TIME=$(grep "实验开始时间" "$LOG_FILE" | awk '{print $3, $4, $5, $6, $7}')
    if [ -n "$START_TIME" ] && [ $COMPLETED -gt 0 ]; then
        START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || echo "0")
        CURRENT_EPOCH=$(date +%s)
        
        if [ "$START_EPOCH" != "0" ]; then
            ELAPSED=$((CURRENT_EPOCH - START_EPOCH))
            AVG_TIME=$((ELAPSED / COMPLETED))
            REMAINING_TIME=$((AVG_TIME * REMAINING))
            
            echo "⏱️  时间估算"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "  开始时间: $START_TIME"
            echo "  已运行: $((ELAPSED / 60)) 分钟"
            echo "  平均每个实验: $((AVG_TIME / 60)) 分钟"
            echo "  预计剩余: $((REMAINING_TIME / 60)) 分钟"
            
            if [ $REMAINING_TIME -gt 0 ]; then
                FINISH_TIME=$(date -d "+${REMAINING_TIME} seconds" "+%Y-%m-%d %H:%M:%S")
                echo "  预计完成: $FINISH_TIME"
            fi
            echo ""
        fi
    fi
    
    # 显示最近完成的实验
    echo "✅ 最近完成的实验"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ls -lt "$RESULTS_DIR"/*.jsonl 2>/dev/null | grep -v "test_" | head -5 | awk '{print "  " $9}' | xargs -I {} basename {}
    echo ""
    
    # 检查错误
    echo "🔍 错误检查"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if tail -100 "$LOG_FILE" | grep -qi "error\|错误\|failed\|exception"; then
        echo "  ⚠️  发现错误！最近的错误信息："
        tail -100 "$LOG_FILE" | grep -i "error\|错误\|failed\|exception" | tail -3 | sed 's/^/  /'
    else
        echo "  ✓ 未发现错误"
    fi
    echo ""
    
    # 检查进程状态
    echo "💻 进程状态"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if ps aux | grep -E "run_pope_combined|run_qwenvl_combined" | grep -v grep > /dev/null; then
        echo "  ✓ 实验进程正在运行"
        PROCESS_COUNT=$(ps aux | grep -E "run_pope_combined|run_qwenvl_combined" | grep -v grep | wc -l)
        echo "  活跃进程数: $PROCESS_COUNT"
    else
        echo "  ⚠️  未检测到实验进程"
    fi
    echo ""
    
    # 记录到监控日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 已完成: $COMPLETED/$TOTAL_EXPERIMENTS ($PROGRESS%)" >> "$MONITOR_LOG"
    
    # 检查是否有新完成的实验
    if [ $COMPLETED -gt $LAST_COMPLETED ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 新完成 $((COMPLETED - LAST_COMPLETED)) 个实验" >> "$MONITOR_LOG"
        LAST_COMPLETED=$COMPLETED
    fi
    
    # 检查是否全部完成
    if [ $COMPLETED -ge $TOTAL_EXPERIMENTS ]; then
        echo "=========================================="
        echo "🎉 所有实验已完成！"
        echo "=========================================="
        echo ""
        echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "总计完成: $COMPLETED 个实验"
        echo ""
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 所有实验完成！" >> "$MONITOR_LOG"
        
        # 生成最终报告
        echo "正在生成综合评估报告..."
        cd /root/autodl-tmp/COMBINED
        python generate_comprehensive_report.py
        
        echo ""
        echo "✅ 综合报告已生成！"
        echo "   - JSON结果: $RESULTS_DIR/comprehensive_results.json"
        echo "   - Markdown报告: $RESULTS_DIR/COMPREHENSIVE_REPORT.md"
        echo ""
        
        break
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "下次更新: 30秒后 (按 Ctrl+C 停止监控)"
    echo ""
    
    # 等待30秒
    sleep 30
done

echo "监控结束"

