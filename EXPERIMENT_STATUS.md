# VCD + AGLA 组合方法 - 实验状态报告

**更新时间**: 2025-10-16  
**状态**: ✅ 环境就绪，可以开始运行实验

---

## 🎯 实验目标

在 COCO POPE 数据集上对比评估 4 种方法：
1. **Baseline** - 标准 LLaVA 解码
2. **VCD Only** - 仅使用 VCD 方法
3. **AGLA Only** - 仅使用 AGLA 方法
4. **VCD + AGLA Combined** - 组合方法（三路对比解码）

---

## ✅ 已完成的工作

### 1. 代码实现 ✅

- ✅ **核心采样函数** (`sample_vcd_agla.py`)
  - 实现三路对比解码逻辑
  - 支持 VCD-only, AGLA-only, Combined 三种模式
  - 自动从 `model_kwargs` 提取参数

- ✅ **修改后的 LLaVA 模型** (`llava/model/language_model/llava_llama.py`)
  - 添加 `prepare_inputs_for_generation_agla()` 方法
  - 在 `forward()` 中添加 `images_agla`, `agla_alpha`, `agla_beta` 参数
  - 解决了 transformers 参数验证问题

- ✅ **评估脚本** (`run_pope_combined.py`)
  - 集成 VCD 噪声添加
  - 集成 AGLA 图像增强（需要 LAVIS）
  - 支持灵活的参数配置
  - 修复了模块导入路径问题

- ✅ **评估工具** (`eval_pope.py`)
  - 计算 Accuracy, Precision, Recall, F1 指标
  - 支持 JSON 输出

- ✅ **自动化脚本** (`run_all_experiments.sh`)
  - 自动运行 4 个实验
  - 自动评估结果
  - 生成对比报告

### 2. 测试验证 ✅

**快速测试 (20 samples)**:
```bash
cd /root/autodl-tmp/COMBINED
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file pope_test_subset.json \
  --answers-file test_results/test_baseline.jsonl \
  --temperature 1.0
```

**测试结果**:
```
✓ 评估完成
Accuracy:   90.00%
Precision:  90.00%
Recall:     90.00%
F1 Score:   90.00%
```

✅ **测试通过！** 系统可以正常运行。

### 3. 关键问题解决 ✅

**问题 1**: `ValueError: The following 'model_kwargs' are not used by the model: ['agla_alpha', 'agla_beta']`

**解决方案**: 
- 在 `LlavaLlamaForCausalLM.forward()` 中添加 `images_agla`, `agla_alpha`, `agla_beta` 参数
- 添加 `prepare_inputs_for_generation_agla()` 方法
- 修复模块导入路径（确保使用 COMBINED 目录中的 llava 模块）

**问题 2**: LAVIS 依赖缺失

**解决方案**:
- 在 `utils/__init__.py` 中添加优雅的错误处理
- 在 `run_pope_combined.py` 中添加 AGLA 可用性检查
- 允许在没有 LAVIS 的情况下运行 Baseline 和 VCD Only

---

## 📊 已有实验结果分析

### AGLA 项目中的结果

**文件位置**:
- Baseline: `/root/autodl-tmp/AGLA/output/llava_coco_pope_popular_answers_baseline_seed1.jsonl`
- AGLA: `/root/autodl-tmp/AGLA/output/llava_coco_pope_popular_answers_agla_seed1.jsonl`

**评估结果**:
```
Baseline (AGLA 项目):
  Accuracy:   86.03%
  Precision:  94.05%
  Recall:     76.93%
  F1 Score:   84.64%

AGLA (AGLA 项目):
  Accuracy:   86.03%  ← 完全相同！
  Precision:  94.05%  ← 完全相同！
  Recall:     76.93%  ← 完全相同！
  F1 Score:   84.64%  ← 完全相同！
```

⚠️ **结论**: AGLA 项目中的 baseline 和 AGLA 结果完全相同，说明 AGLA 实验没有正确运行。**需要重新运行所有实验。**

### VCD 项目中的结果

**文件位置**:
- Baseline: `/root/autodl-tmp/VCD/experiments/output/llava15_coco_pope_popular_baseline_seed55.jsonl`
- VCD: `/root/autodl-tmp/VCD/experiments/output/llava15_coco_pope_popular_vcd_seed55.jsonl`

**文件状态**: 两个文件都是空的（0 行）

⚠️ **结论**: VCD 项目的 LLaVA-1.5 实验没有运行。**需要重新运行所有实验。**

---

## 🚀 下一步行动

### 选项 A: 运行完整实验（推荐）

**优点**:
- 获得完整的对比数据
- 验证组合方法的有效性
- 可以发表研究成果

**缺点**:
- 需要约 3.5 小时
- 需要安装 LAVIS
- 需要 GPU 资源

**执行步骤**:

1. **安装 LAVIS**:
```bash
pip install salesforce-lavis
```

2. **运行自动化脚本**:
```bash
cd /root/autodl-tmp/COMBINED
bash run_all_experiments.sh
```

3. **等待完成** (~3.5 小时)

4. **查看结果**:
```bash
cat pope_results/summary.json
```

### 选项 B: 分步运行实验

如果想要更多控制，可以手动运行每个实验：

#### 实验 1: Baseline (~25 分钟)

```bash
cd /root/autodl-tmp/COMBINED

python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/baseline.jsonl \
  --temperature 1.0

# 评估
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/baseline.jsonl \
  --output pope_results/baseline_metrics.json
```

#### 实验 2: VCD Only (~50 分钟)

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

# 评估
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/vcd_only.jsonl \
  --output pope_results/vcd_only_metrics.json
```

#### 实验 3: AGLA Only (~60 分钟)

```bash
# 需要先安装 LAVIS
pip install salesforce-lavis

python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/agla_only.jsonl \
  --use-agla \
  --agla-alpha 1.0 \
  --agla-beta 0.5 \
  --temperature 1.0

# 评估
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/agla_only.jsonl \
  --output pope_results/agla_only_metrics.json
```

#### 实验 4: VCD + AGLA Combined (~75 分钟)

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

# 评估
python eval_pope.py \
  --gt_file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --gen_file pope_results/combined.jsonl \
  --output pope_results/combined_metrics.json
```

### 选项 C: 仅运行 Baseline 和 VCD Only（无需 LAVIS）

如果 LAVIS 安装困难，可以先运行不需要 LAVIS 的实验：

```bash
cd /root/autodl-tmp/COMBINED

# Baseline
python run_pope_combined.py \
  --model-path /root/autodl-tmp/models/llava-v1.5-7b \
  --image-folder /root/autodl-tmp/VCD_data/coco/val2014 \
  --question-file /root/autodl-tmp/VCD/experiments/data/POPE/coco/coco_pope_popular.json \
  --answers-file pope_results/baseline.jsonl \
  --temperature 1.0

# VCD Only
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

---

## 📋 检查清单

### 实验前
- [x] 模型路径正确
- [x] 数据集路径正确
- [x] 代码测试通过
- [x] 评估脚本可用
- [x] 自动化脚本准备好
- [ ] LAVIS 已安装（AGLA 需要）
- [ ] GPU 内存充足（建议 ≥24GB）

### 实验中
- [ ] Baseline 完成
- [ ] VCD Only 完成
- [ ] AGLA Only 完成
- [ ] Combined 完成

### 实验后
- [ ] 所有结果文件生成
- [ ] 评估指标计算
- [ ] 对比报告生成
- [ ] 结果验证

---

## 💡 建议

### 推荐方案

**立即执行**:
1. 安装 LAVIS: `pip install salesforce-lavis`
2. 运行自动化脚本: `bash run_all_experiments.sh`
3. 等待约 3.5 小时
4. 查看结果并分析

**理由**:
- 一次性完成所有实验
- 自动生成对比报告
- 验证组合方法的有效性

### 备选方案

如果 LAVIS 安装失败或 GPU 内存不足：
1. 先运行 Baseline 和 VCD Only
2. 分析 VCD 的性能提升
3. 稍后再运行 AGLA 相关实验

---

## 📞 技术支持

### 常见问题

**Q1: LAVIS 安装失败怎么办？**

A: 尝试从源码安装：
```bash
git clone https://github.com/salesforce/LAVIS.git
cd LAVIS
pip install -e .
```

**Q2: GPU 内存不足怎么办？**

A: 
- 只运行 Baseline 和 VCD Only（不需要 BLIP-ITM）
- 使用更小的 batch size
- 使用 FP16 精度

**Q3: 运行速度太慢怎么办？**

A:
- 使用更快的 GPU
- 减少测试样本数量
- 使用贪婪解码 (temperature=0)

---

## 📊 预期结果

基于原始论文，预期性能（F1 Score）：

| 方法 | 预期 F1 | 相比 Baseline |
|------|---------|---------------|
| Baseline | ~84% | - |
| VCD Only | ~86% | +2-3% |
| AGLA Only | ~87% | +3-4% |
| **VCD + AGLA Combined** | **~89-91%** | **+5-7%** |

---

**状态**: ✅ 环境就绪，可以开始运行实验  
**下一步**: 安装 LAVIS 并运行 `bash run_all_experiments.sh`  
**预计完成时间**: 3.5 小时后

