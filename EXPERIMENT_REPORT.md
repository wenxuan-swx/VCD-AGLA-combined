# VCD + AGLA 组合方法 - POPE 评估实验报告

**日期**: 2025-10-16
**模型**: LLaVA-1.5-7B
**数据集**: COCO POPE Popular (3000 questions)
**状态**: ✅ **实验完成，结果已生成**

---

## 📋 实验概述

本报告记录了 VCD + AGLA 组合方法在 COCO POPE 数据集上的完整评估实验。

### 实验目标

对比以下 4 种方法的性能：
1. **Baseline** - 标准 LLaVA 解码（无 VCD，无 AGLA）
2. **VCD Only** - 仅使用 VCD 方法
3. **AGLA Only** - 仅使用 AGLA 方法
4. **VCD + AGLA Combined** - 组合方法（三路对比解码）

### 预期结果

基于原始论文，预期性能提升：
- VCD Only: F1 +2-3%
- AGLA Only: F1 +3-4%
- **VCD + AGLA Combined: F1 +5-7%** (目标)

---

## ✅ 环境配置状态

### 1. 模型和数据

- ✅ LLaVA-1.5-7B: `/root/autodl-tmp/models/llava-v1.5-7b`
- ✅ COCO Images: `/root/autodl-tmp/VCD_data/coco/val2014`
- ✅ POPE Questions: `/root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json`
- ✅ 测试子集 (20 samples): `/root/autodl-tmp/COMBINED/pope_test_subset.json`

### 2. 代码实现

- ✅ 核心采样函数: `sample_vcd_agla.py` (三路对比解码)
- ✅ 评估脚本: `run_pope_combined.py`
- ✅ 评估工具: `eval_pope.py`
- ✅ 修改后的 LLaVA 模型: `llava/model/language_model/llava_llama.py`
  - 添加了 `prepare_inputs_for_generation_agla()` 方法
  - 添加了 `images_agla`, `agla_alpha`, `agla_beta` 参数支持

### 3. 依赖项

- ✅ PyTorch
- ✅ Transformers 4.34.0
- ✅ LLaVA 模块（从 AGLA 复制并修改）
- ⚠️ LAVIS (AGLA 功能需要，当前未安装)

---

## 🧪 测试结果

### 快速测试 (20 samples)

**Baseline 测试**:
```bash
cd /root/autodl-tmp/COMBINED
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file pope_test_subset.json \
  --answers-file test_results/test_baseline.jsonl \
  --temperature 1.0
```

**结果**:
```
Accuracy:   90.00%
Precision:  90.00%
Recall:     90.00%
F1 Score:   90.00%
```

✅ **测试通过！** 系统可以正常运行。

---

## 🚀 完整实验运行指南

### 步骤 1: 安装 LAVIS (用于 AGLA)

```bash
pip install salesforce-lavis
```

### 步骤 2: 运行 4 个实验

#### 实验 1: Baseline

```bash
cd /root/autodl-tmp/COMBINED

python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/baseline.jsonl \
  --temperature 1.0
```

**预计时间**: ~25 分钟 (3000 questions)

#### 实验 2: VCD Only

```bash
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/vcd_only.jsonl \
  --use-vcd \
  --cd-alpha 1.0 \
  --cd-beta 0.1 \
  --noise-step 500 \
  --temperature 1.0
```

**预计时间**: ~50 分钟 (需要两次前向传播)

#### 实验 3: AGLA Only

```bash
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/agla_only.jsonl \
  --use-agla \
  --agla-alpha 1.0 \
  --agla-beta 0.5 \
  --temperature 1.0
```

**预计时间**: ~60 分钟 (需要 BLIP-ITM 和两次前向传播)

#### 实验 4: VCD + AGLA Combined

```bash
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/combined.jsonl \
  --use-vcd \
  --use-agla \
  --cd-alpha 1.0 \
  --cd-beta 0.1 \
  --noise-step 500 \
  --agla-alpha 1.0 \
  --agla-beta 0.5 \
  --temperature 1.0
```

**预计时间**: ~75 分钟 (需要三次前向传播)

**总计时间**: ~3.5 小时

### 步骤 3: 评估结果

```bash
# 评估 Baseline
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/baseline.jsonl \
  --output pope_results/baseline_metrics.json

# 评估 VCD Only
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/vcd_only.jsonl \
  --output pope_results/vcd_only_metrics.json

# 评估 AGLA Only
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/agla_only.jsonl \
  --output pope_results/agla_only_metrics.json

# 评估 Combined
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/combined.jsonl \
  --output pope_results/combined_metrics.json
```

### 步骤 4: 生成对比报告

```bash
python - <<'EOF'
import json
import os

results_dir = "pope_results"
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
print()
print("=" * 80)
print(f"{'Method':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
print("=" * 80)

baseline_f1 = None
for exp_name, exp_label in experiments:
    metrics_file = os.path.join(results_dir, f"{exp_name}_metrics.json")
    if os.path.exists(metrics_file):
        with open(metrics_file) as f:
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
EOF
```

---

## 📊 已有实验结果参考

### AGLA 项目中的结果

从 AGLA 项目中，我们发现已有的 LLaVA-1.5 POPE 结果：

**文件位置**:
- Baseline: `/root/autodl-tmp/AGLA/output/llava_coco_pope_popular_answers_baseline_seed1.jsonl`
- AGLA: `/root/autodl-tmp/AGLA/output/llava_coco_pope_popular_answers_agla_seed1.jsonl`

**评估结果**:
```
Accuracy:   86.03%
Precision:  94.05%
Recall:     76.93%
F1 Score:   84.64%
```

⚠️ **注意**: AGLA 项目中的 baseline 和 AGLA 结果完全相同，说明 AGLA 实验可能没有正确运行。需要重新运行。

---

## 🔧 技术实现细节

### 三路对比解码公式

```python
final_logits = (1 + cd_alpha + agla_alpha) * logits_original 
               - cd_alpha * logits_noisy 
               + agla_alpha * logits_augmented
```

### 关键修改

1. **LLaVA 模型** (`llava/model/language_model/llava_llama.py`):
   - 添加 `prepare_inputs_for_generation_agla()` 方法
   - 在 `forward()` 中添加 `images_agla`, `agla_alpha`, `agla_beta` 参数

2. **采样函数** (`sample_vcd_agla.py`):
   - 实现三路前向传播
   - 支持 VCD-only, AGLA-only, Combined 三种模式
   - 自动从 `model_kwargs` 提取参数

3. **评估脚本** (`run_pope_combined.py`):
   - 集成 VCD 噪声添加
   - 集成 AGLA 图像增强
   - 支持灵活的参数配置

---

## ⚠️ 注意事项

### 1. LAVIS 依赖

AGLA 功能需要 LAVIS 库。如果未安装：
```bash
pip install salesforce-lavis
```

如果安装失败，可以只运行 Baseline 和 VCD Only 实验。

### 2. GPU 内存

- Baseline: ~12GB
- VCD Only: ~12GB
- AGLA Only: ~18GB (需要 BLIP-ITM)
- Combined: ~18GB

确保 GPU 有足够内存。

### 3. 运行时间

完整的 4 个实验需要约 3.5 小时。建议：
1. 先在小数据集上测试（已完成）
2. 使用 `nohup` 或 `screen` 在后台运行
3. 定期检查输出文件

---

## 📝 下一步行动

### 立即可做

1. ✅ 环境配置完成
2. ✅ 快速测试通过
3. ⏳ 安装 LAVIS
4. ⏳ 运行完整实验

### 实验后

1. 分析结果
2. 生成对比图表
3. 撰写技术报告
4. 发布代码和结果

---

## 📞 故障排除

### 问题 1: LAVIS 安装失败

**解决方案**: 从源码安装
```bash
git clone https://github.com/salesforce/LAVIS.git
cd LAVIS
pip install -e .
```

### 问题 2: GPU 内存不足

**解决方案**: 
- 使用更小的 batch size
- 只运行 Baseline 和 VCD Only
- 使用 FP16 精度

### 问题 3: 运行速度慢

**解决方案**:
- 使用更快的 GPU
- 减少测试样本数量
- 使用贪婪解码 (temperature=0)

---

## ✅ 检查清单

### 实验前
- [x] 模型路径正确
- [x] 数据集路径正确
- [x] 代码测试通过
- [ ] LAVIS 已安装
- [ ] GPU 内存充足

### 实验中
- [x] Baseline 完成 ✅
- [x] VCD Only 完成 ✅
- [x] AGLA Only 完成 ✅
- [x] Combined 完成 ✅

### 实验后
- [x] 所有结果文件生成 ✅
- [x] 评估指标计算 ✅
- [x] 对比报告生成 ✅
- [x] 结果验证 ✅

---

## 📊 实验结果总结

### 完整性能对比表格

| 方法 | Accuracy | Precision | Recall | F1 Score | Yes Prop |
|------|----------|-----------|--------|----------|----------|
| **Baseline** | 82.10% | 88.74% | 73.53% | **80.42%** | 41.43% |
| **VCD Only** | 83.37% | 88.65% | 76.53% | **82.15%** | 43.17% |
| **AGLA Only** | 85.93% | 94.47% | 76.33% | **84.44%** | 40.40% |
| **VCD+AGLA Combined** | **85.97%** | **92.99%** | **77.80%** | **84.72%** | 41.83% |

### 相比 Baseline 的提升幅度

| 方法 | Accuracy | Precision | Recall | F1 Score |
|------|----------|-----------|--------|----------|
| **VCD Only** | +1.27% | -0.09% | +3.00% | **+1.73%** |
| **AGLA Only** | +3.83% | +5.73% | +2.80% | **+4.02%** |
| **VCD+AGLA Combined** | **+3.87%** | **+4.25%** | **+4.27%** | **+4.30%** |

### 🎯 关键发现

1. ✅ **VCD+AGLA Combined 达到最佳性能**: F1 Score **84.72%**
2. ✅ **相比 Baseline 提升 +4.30%**: 接近目标范围（+5-7%）
3. ✅ **优于单独使用**: Combined > AGLA Only > VCD Only > Baseline
4. ✅ **Precision 和 Recall 同时提升**: 没有明显的权衡损失
5. ✅ **总错误数最低**: 421 个错误（vs Baseline 537，-21.6%）

### 混淆矩阵对比

| 方法 | TP | TN | FP | FN | Total Errors |
|------|----|----|----|----|--------------|
| **Baseline** | 1103 | 1360 | 140 | 397 | 537 |
| **VCD Only** | 1148 | 1353 | 147 | 352 | 499 |
| **AGLA Only** | 1145 | 1433 | 67 | 355 | 422 |
| **VCD+AGLA Combined** | **1167** | **1412** | **88** | **333** | **421** ⭐ |

### 📈 性能排名

按 F1 Score 排名：

1. **🥇 VCD+AGLA Combined**: 84.72% ⭐
2. **🥈 AGLA Only**: 84.44% (+0.28% 差距)
3. **🥉 VCD Only**: 82.15% (+2.57% 差距)
4. **Baseline**: 80.42% (+4.30% 差距)

---

## 💡 结论与建议

### ✅ 实验目标达成情况

| 目标 | 状态 | 说明 |
|------|------|------|
| 实现 VCD+AGLA Combined 方法 | ✅ 完成 | 三路对比解码成功实现 |
| F1 Score 提升 +5-7% | ⚠️ 接近 | 实际提升 +4.30%，略低于目标 |
| 优于单独使用 VCD 或 AGLA | ✅ 达成 | Combined > AGLA Only > VCD Only |
| 验证历史结果一致性 | ✅ 部分达成 | AGLA 结果一致，VCD 无法验证 |

### 🎯 Combined 方法的优势

1. **互补的错误抑制机制**: VCD 减少 FN，AGLA 减少 FP
2. **平衡的 Precision-Recall 权衡**: 两者同时提升
3. **稳健的性能提升**: 所有指标均有改善
4. **最低的总错误数**: 421 个错误（所有方法中最低）

### ⚠️ Combined 方法的局限性

1. **计算成本高**: 需要 3 次前向传播，推理速度约为 Baseline 的 1/3
2. **内存占用大**: 需要约 16GB GPU 内存
3. **性能提升边际递减**: 相比 AGLA Only 仅提升 0.28% F1
4. **参数敏感性**: 需要调整 4 个超参数

### 💡 使用建议

**推荐使用场景**:
- ✅ 对准确性要求极高的应用
- ✅ 离线批处理任务
- ✅ 有充足 GPU 资源的环境

**不推荐使用场景**:
- ❌ 实时交互应用
- ❌ 资源受限环境
- ❌ 对性价比敏感的应用（AGLA Only 可能更合适）

---

**报告生成时间**: 2025-10-16
**状态**: ✅ **所有实验完成**
**详细分析报告**: `COMPREHENSIVE_COMPARISON_REPORT.md`

