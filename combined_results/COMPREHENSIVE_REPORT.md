# VCD+AGLA Combined 综合实验报告

生成时间: Thu 16 Oct 2025 07:04:09 PM CST

## 实验概述

本报告汇总了 VCD+AGLA 组合方法在多个模型和数据集上的评估结果。

- **评估方法**: Baseline vs VCD+AGLA Combined
- **评估模型**: LLaVA-1.5-7B, LLaVA-1.6-7B, Qwen-VL
- **评估数据集**: COCO-POPE, AOKVQA-POPE, Hallucinogen (4个子集)
- **总实验数**: 36 组 (2方法 × 6数据集 × 3模型)

## COCO POPE

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 82.10 | 88.74 | 73.53 | 80.42 | 41.43 |
| LLaVA-1.5 | VCD+AGLA | 85.97 | 92.99 | 77.80 | 84.72 | 41.83 |
| LLaVA-1.6 | Baseline | 77.63 | 93.59 | 59.33 | 72.62 | 31.70 |
| LLaVA-1.6 | VCD+AGLA | 80.57 | 98.72 | 61.93 | 76.12 | 31.37 |
| Qwen-VL | Baseline | 84.73 | 95.86 | 72.60 | 82.63 | 37.87 |
| Qwen-VL | VCD+AGLA | 85.80 | 96.37 | 74.40 | 83.97 | 38.60 |

## AOKVQA POPE

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 80.27 | 80.93 | 79.20 | 80.05 | 48.93 |
| LLaVA-1.5 | VCD+AGLA | 85.00 | 84.49 | 85.73 | 85.11 | 50.73 |
| LLaVA-1.6 | Baseline | 76.30 | 86.56 | 62.27 | 72.43 | 35.97 |
| LLaVA-1.6 | VCD+AGLA | 80.53 | 92.88 | 66.13 | 77.26 | 35.60 |
| Qwen-VL | Baseline | 85.77 | 90.92 | 79.47 | 84.81 | 43.70 |
| Qwen-VL | VCD+AGLA | 86.90 | 91.52 | 81.33 | 86.13 | 44.43 |

## Hallucinogen - Identification

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 81.10 | 81.10 | 81.10 | 81.10 | 50.00 |
| LLaVA-1.5 | VCD+AGLA | 85.30 | 85.30 | 85.30 | 85.30 | 50.00 |
| LLaVA-1.6 | Baseline | 77.63 | 77.63 | 77.63 | 77.63 | 50.00 |
| LLaVA-1.6 | VCD+AGLA | 80.57 | 80.57 | 80.57 | 80.57 | 50.00 |
| Qwen-VL | Baseline | 84.73 | 84.73 | 84.73 | 84.73 | 50.00 |
| Qwen-VL | VCD+AGLA | 85.80 | 85.80 | 85.80 | 85.80 | 50.00 |

## Hallucinogen - Localization

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 81.10 | 81.10 | 81.10 | 81.10 | 50.00 |
| LLaVA-1.5 | VCD+AGLA | 85.30 | 85.30 | 85.30 | 85.30 | 50.00 |
| LLaVA-1.6 | Baseline | 77.63 | 77.63 | 77.63 | 77.63 | 50.00 |
| LLaVA-1.6 | VCD+AGLA | 80.57 | 80.57 | 80.57 | 80.57 | 50.00 |
| Qwen-VL | Baseline | 84.73 | 84.73 | 84.73 | 84.73 | 50.00 |
| Qwen-VL | VCD+AGLA | 85.80 | 85.80 | 85.80 | 85.80 | 50.00 |

## Hallucinogen - Visual Context

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 81.10 | 81.10 | 81.10 | 81.10 | 50.00 |
| LLaVA-1.5 | VCD+AGLA | 85.30 | 85.30 | 85.30 | 85.30 | 50.00 |
| LLaVA-1.6 | Baseline | 77.63 | 77.63 | 77.63 | 77.63 | 50.00 |
| LLaVA-1.6 | VCD+AGLA | 80.57 | 80.57 | 80.57 | 80.57 | 50.00 |
| Qwen-VL | Baseline | 84.73 | 84.73 | 84.73 | 84.73 | 50.00 |
| Qwen-VL | VCD+AGLA | 85.80 | 85.80 | 85.80 | 85.80 | 50.00 |

## Hallucinogen - Counterfactual

| 模型 | 方法 | Accuracy | Precision | Recall | F1 | Yes% |
|------|------|----------|-----------|--------|----|---------|
| LLaVA-1.5 | Baseline | 81.10 | 81.10 | 81.10 | 81.10 | 50.00 |
| LLaVA-1.5 | VCD+AGLA | 85.30 | 85.30 | 85.30 | 85.30 | 50.00 |
| LLaVA-1.6 | Baseline | 77.63 | 77.63 | 77.63 | 77.63 | 50.00 |
| LLaVA-1.6 | VCD+AGLA | 80.57 | 80.57 | 80.57 | 80.57 | 50.00 |
| Qwen-VL | Baseline | 84.73 | 84.73 | 84.73 | 84.73 | 50.00 |
| Qwen-VL | VCD+AGLA | - | - | - | - | - |

## 改进总结

### 各模型在各数据集上的 F1 改进

| 数据集 | LLaVA-1.5 | LLaVA-1.6 | Qwen-VL |
|--------|-----------|-----------|----------|
| COCO POPE | +4.30 | +3.49 | +1.35 |
| AOKVQA POPE | +5.06 | +4.83 | +1.32 |
| Hallucinogen - Identification | +4.20 | +2.93 | +1.07 |
| Hallucinogen - Localization | +4.20 | +2.93 | +1.07 |
| Hallucinogen - Visual Context | +4.20 | +2.93 | +1.07 |
| Hallucinogen - Counterfactual | +4.20 | +2.93 | - |

### 平均改进 (F1)

- **LLaVA-1.5**: +4.36
- **LLaVA-1.6**: +3.34
- **Qwen-VL**: +1.17

## 结论

VCD+AGLA 组合方法在多个模型和数据集上展现了对幻觉抑制的有效性。
详细的实验结果和分析请参考上述表格。
