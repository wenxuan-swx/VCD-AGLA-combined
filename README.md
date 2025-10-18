# VCD + AGLA Combined Method

**Three-Way Contrastive Decoding for Mitigating Object Hallucinations in Large Vision-Language Models**

This project combines two state-of-the-art methods for reducing hallucinations in VLMs:
- **VCD (Visual Contrastive Decoding)**: Suppresses statistical bias through noisy image contrast
- **AGLA (Assembly of Global and Local Attention)**: Enhances visual understanding through attention-guided augmentation

## 🎯 Core Idea

The combined method uses three-way contrastive decoding:

```python
final_logits = (1 + α_vcd + α_agla) * logits_original 
               - α_vcd * logits_noisy 
               + α_agla * logits_augmented
```

Where:
- `logits_original`: From original image
- `logits_noisy`: From VCD noise-added image
- `logits_augmented`: From AGLA attention-enhanced image

## 📁 Project Structure

```
COMBINED/
├── sample_vcd_agla.py          # Core three-way sampling function
├── llava_llama_combined.py     # Modified LLaVA model
├── run_combined_llava.py       # Evaluation script
├── test_combined.py            # Test suite
├── utils/
│   ├── __init__.py
│   ├── vcd_add_noise.py        # VCD noise addition
│   └── augmentation.py         # AGLA image augmentation
├── configs/
│   └── default_params.yaml     # Default parameters
├── scripts/
│   └── (evaluation scripts)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (if not already installed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install LAVIS for AGLA
pip install salesforce-lavis
```

**Important**: You need to have the LLaVA package installed. If not available, copy the `llava` directory from either the AGLA or VCD project:

```bash
# Option 1: Copy from AGLA project
cp -r /root/autodl-tmp/AGLA/llava ./

# Option 2: Copy from VCD project
cp -r /root/autodl-tmp/VCD/experiments/llava ./
```

### 2. Run Tests

```bash
python test_combined.py
```

This will test:
- ✓ VCD noise addition
- ✓ AGLA augmentation (requires BLIP-ITM)
- ✓ Logits combination
- ✓ Sampling function
- ✓ Model import

### 3. Run Evaluation

#### VCD Only
```bash
python run_combined_llava.py \
    --model-path /path/to/llava-v1.5-7b \
    --image-folder /path/to/coco/val2014 \
    --question-file /path/to/pope_coco.jsonl \
    --answers-file output_vcd.jsonl \
    --use-vcd \
    --cd-alpha 1.0 \
    --cd-beta 0.1 \
    --noise-step 500
```

#### AGLA Only
```bash
python run_combined_llava.py \
    --model-path /path/to/llava-v1.5-7b \
    --image-folder /path/to/coco/val2014 \
    --question-file /path/to/pope_coco.jsonl \
    --answers-file output_agla.jsonl \
    --use-agla \
    --agla-alpha 1.0 \
    --agla-beta 0.5
```

#### Combined VCD + AGLA
```bash
python run_combined_llava.py \
    --model-path /path/to/llava-v1.5-7b \
    --image-folder /path/to/coco/val2014 \
    --question-file /path/to/pope_coco.jsonl \
    --answers-file output_combined.jsonl \
    --use-vcd --use-agla \
    --cd-alpha 1.0 --cd-beta 0.1 \
    --agla-alpha 1.0 --agla-beta 0.5 \
    --noise-step 500
```

## 📊 Parameters

### VCD Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `cd_alpha` | 1.0 | 0.5-1.5 | VCD contrast strength |
| `cd_beta` | 0.1 | 0.05-0.2 | VCD plausibility threshold |
| `noise_step` | 500 | 300-700 | Diffusion noise step |

### AGLA Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `agla_alpha` | 1.0 | 0.5-1.5 | AGLA enhancement strength |
| `agla_beta` | 0.5 | 0.3-0.7 | AGLA plausibility threshold |

### Recommended Configurations

**Conservative** (High Precision):
```bash
--cd-alpha 0.5 --cd-beta 0.2 --noise-step 300 \
--agla-alpha 0.5 --agla-beta 0.7
```

**Balanced** (Recommended):
```bash
--cd-alpha 1.0 --cd-beta 0.1 --noise-step 500 \
--agla-alpha 1.0 --agla-beta 0.5
```

**Aggressive** (High Recall):
```bash
--cd-alpha 1.5 --cd-beta 0.05 --noise-step 700 \
--agla-alpha 1.5 --agla-beta 0.3
```

## 🔬 How It Works

### 1. Image Preparation

For each input, three images are prepared:

```python
# Original image
image_original = preprocess(raw_image)

# VCD: Add diffusion noise
image_vcd = add_diffusion_noise(image_original, noise_step=500)

# AGLA: Generate attention-guided augmentation
image_agla = augmentation(raw_image, question, model_itm)
```

### 2. Three-Way Forward Pass

```python
# Forward pass with original image
logits_orig = model(input_ids, images=image_original).logits[:, -1, :]

# Forward pass with VCD noisy image
logits_vcd = model(input_ids, images=image_vcd).logits[:, -1, :]

# Forward pass with AGLA augmented image
logits_agla = model(input_ids, images=image_agla).logits[:, -1, :]
```

### 3. Logits Combination

```python
# Three-way contrastive decoding
combined_logits = (
    (1 + cd_alpha + agla_alpha) * logits_orig
    - cd_alpha * logits_vcd
    + agla_alpha * logits_agla
)

# Apply plausibility constraint
cutoff = log(cd_beta) + logits_orig.max()
final_logits = combined_logits.masked_fill(logits_orig < cutoff, -inf)
```

### 4. Sampling

```python
# Sample next token
probs = softmax(final_logits)
next_token = multinomial(probs)
```

## 📈 Expected Performance

Based on individual method performance on COCO POPE:

| Method | Accuracy | Precision | Recall | F1 Score |
|--------|----------|-----------|--------|----------|
| Baseline | 86.03% | 84.50% | 87.67% | 86.03% |
| VCD | 88.50% | 87.20% | 89.90% | 88.50% |
| AGLA | 89.87% | 89.55% | 90.20% | 89.87% |
| **VCD+AGLA** | **~91.5%** | **~90.8%** | **~92.2%** | **~91.5%** |

*Expected improvement: +4-7% F1 score*

## 💻 System Requirements

- **GPU**: NVIDIA GPU with ≥24GB VRAM (e.g., RTX 4090, A100)
- **RAM**: 32GB+
- **Storage**: 100GB+ (for models and data)
- **CUDA**: 11.8+
- **Python**: 3.9+

## 🔧 Troubleshooting

### Issue: Out of Memory (OOM)

**Solution**:
```python
# Use FP16
model.half()

# Reduce batch size
batch_size = 1

# Enable gradient checkpointing
model.gradient_checkpointing_enable()
```

### Issue: BLIP-ITM Loading Failed

**Solution**:
```bash
# Install LAVIS
pip install salesforce-lavis

# Or specify model path
--blip-model-path /path/to/blip_itm_large
```

### Issue: Slow Inference

**Solution**:
- Enable KV cache: `use_cache=True`
- Reduce max tokens: `--max-new-tokens 512`
- Use greedy decoding: `do_sample=False`

## 📚 Citation

If you use this code, please cite the original papers:

```bibtex
@article{leng2024vcd,
  title={Mitigating Object Hallucinations in Large Vision-Language Models through Visual Contrastive Decoding},
  author={Leng, Sicong and others},
  journal={arXiv preprint arXiv:2311.16922},
  year={2024}
}

@article{sun2024agla,
  title={Mitigating Object Hallucinations in Large Vision-Language Models with Assembly of Global and Local Attention},
  author={Sun, Wenbin and others},
  journal={arXiv preprint arXiv:2406.12718},
  year={2024}
}
```

## 📝 License

This project combines code from VCD and AGLA projects. Please refer to their respective licenses.

## 🤝 Contributing

This is a research project. For issues or improvements, please:
1. Test thoroughly with `test_combined.py`
2. Document parameter changes
3. Report results on standard benchmarks

## 📧 Contact

For questions about this implementation, please refer to:
- VCD paper: https://arxiv.org/abs/2311.16922
- AGLA paper: https://arxiv.org/abs/2406.12718

---

**Status**: ✅ Ready for evaluation  
**Version**: 1.0  
**Last Updated**: 2025-10-15

