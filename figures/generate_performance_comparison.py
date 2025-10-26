#!/usr/bin/env python3
"""
Generate performance comparison bar charts for VCD+AGLA paper.
Compares Baseline vs Combined method across models and datasets.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Set publication-quality parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Load data
data_path = '../combined_results/comprehensive_results.json'
with open(data_path, 'r') as f:
    data = json.load(f)

# Model names mapping
model_names = {
    'llava15': 'LLaVA-1.5-7B',
    'llava16': 'LLaVA-1.6-7B',
    'qwenvl': 'Qwen-VL'
}

# Dataset names mapping
dataset_names = {
    'coco_pope': 'COCO-POPE',
    'aokvqa_pope': 'AOKVQA-POPE',
    'hallucinogen_identification': 'Hallucinogen-ID',
    'hallucinogen_localization': 'Hallucinogen-Loc',
    'hallucinogen_visual_context': 'Hallucinogen-VC',
    'hallucinogen_counterfactual': 'Hallucinogen-CF'
}

def generate_f1_comparison_by_model():
    """Generate F1 score comparison grouped by model."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    for idx, (model_key, model_name) in enumerate(model_names.items()):
        ax = axes[idx]
        
        # Extract data for this model
        datasets = []
        baseline_f1 = []
        combined_f1 = []
        improvements = []
        
        for dataset_key, dataset_name in dataset_names.items():
            if dataset_key in data[model_key]:
                datasets.append(dataset_name)
                baseline_f1.append(data[model_key][dataset_key]['baseline']['f1'])
                combined_f1.append(data[model_key][dataset_key]['combined']['f1'])
                improvements.append(combined_f1[-1] - baseline_f1[-1])
        
        # Create bar chart
        x = np.arange(len(datasets))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, baseline_f1, width, label='Baseline', 
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, combined_f1, width, label='VCD+AGLA', 
                       color='#e74c3c', alpha=0.8)
        
        # Add improvement annotations
        for i, (b1, b2, imp) in enumerate(zip(bars1, bars2, improvements)):
            height = max(b1.get_height(), b2.get_height())
            ax.text(i, height + 1, f'+{imp:.2f}%', 
                   ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax.set_xlabel('Dataset')
        ax.set_ylabel('F1 Score (%)')
        ax.set_title(model_name)
        ax.set_xticks(x)
        ax.set_xticklabels(datasets, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig('f1_comparison_by_model.png', bbox_inches='tight')
    plt.savefig('f1_comparison_by_model.pdf', bbox_inches='tight')
    print("Generated: f1_comparison_by_model.png/pdf")
    plt.close()

def generate_f1_comparison_by_dataset():
    """Generate F1 score comparison grouped by dataset (POPE only)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    pope_datasets = ['coco_pope', 'aokvqa_pope']
    
    for idx, dataset_key in enumerate(pope_datasets):
        ax = axes[idx]
        
        # Extract data for this dataset
        models = []
        baseline_f1 = []
        combined_f1 = []
        improvements = []
        
        for model_key, model_name in model_names.items():
            if dataset_key in data[model_key]:
                models.append(model_name)
                baseline_f1.append(data[model_key][dataset_key]['baseline']['f1'])
                combined_f1.append(data[model_key][dataset_key]['combined']['f1'])
                improvements.append(combined_f1[-1] - baseline_f1[-1])
        
        # Create bar chart
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, baseline_f1, width, label='Baseline', 
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, combined_f1, width, label='VCD+AGLA', 
                       color='#e74c3c', alpha=0.8)
        
        # Add improvement annotations
        for i, (b1, b2, imp) in enumerate(zip(bars1, bars2, improvements)):
            height = max(b1.get_height(), b2.get_height())
            ax.text(i, height + 1, f'+{imp:.2f}%', 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Model')
        ax.set_ylabel('F1 Score (%)')
        ax.set_title(dataset_names[dataset_key])
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig('f1_comparison_by_dataset.png', bbox_inches='tight')
    plt.savefig('f1_comparison_by_dataset.pdf', bbox_inches='tight')
    print("Generated: f1_comparison_by_dataset.png/pdf")
    plt.close()

def generate_metrics_comparison():
    """Generate comprehensive metrics comparison for LLaVA-1.5 on COCO-POPE."""
    model_key = 'llava15'
    dataset_key = 'coco_pope'
    
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    
    baseline_values = [data[model_key][dataset_key]['baseline'][m] for m in metrics]
    combined_values = [data[model_key][dataset_key]['combined'][m] for m in metrics]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline', 
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, combined_values, width, label='VCD+AGLA', 
                   color='#e74c3c', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Metric')
    ax.set_ylabel('Score (%)')
    ax.set_title('Performance Metrics Comparison (LLaVA-1.5 on COCO-POPE)')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig('metrics_comparison_llava15_coco.png', bbox_inches='tight')
    plt.savefig('metrics_comparison_llava15_coco.pdf', bbox_inches='tight')
    print("Generated: metrics_comparison_llava15_coco.png/pdf")
    plt.close()

def generate_improvement_heatmap():
    """Generate heatmap of F1 improvements across models and datasets."""
    import matplotlib.colors as mcolors
    
    # Prepare data matrix
    models_list = list(model_names.keys())
    datasets_list = list(dataset_names.keys())
    
    improvement_matrix = np.zeros((len(models_list), len(datasets_list)))
    
    for i, model_key in enumerate(models_list):
        for j, dataset_key in enumerate(datasets_list):
            if dataset_key in data[model_key]:
                baseline = data[model_key][dataset_key]['baseline']['f1']
                combined = data[model_key][dataset_key]['combined']['f1']
                improvement_matrix[i, j] = combined - baseline
            else:
                improvement_matrix[i, j] = np.nan
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Create custom colormap (white to red)
    cmap = plt.cm.Reds
    
    im = ax.imshow(improvement_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=6)
    
    # Set ticks
    ax.set_xticks(np.arange(len(datasets_list)))
    ax.set_yticks(np.arange(len(models_list)))
    ax.set_xticklabels([dataset_names[k] for k in datasets_list], rotation=45, ha='right')
    ax.set_yticklabels([model_names[k] for k in models_list])
    
    # Add text annotations
    for i in range(len(models_list)):
        for j in range(len(datasets_list)):
            if not np.isnan(improvement_matrix[i, j]):
                text = ax.text(j, i, f'{improvement_matrix[i, j]:.2f}%',
                             ha="center", va="center", color="black", fontsize=9)
    
    ax.set_title('F1 Score Improvement: VCD+AGLA vs Baseline (%)')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('F1 Improvement (%)', rotation=270, labelpad=20)
    
    plt.tight_layout()
    plt.savefig('improvement_heatmap.png', bbox_inches='tight')
    plt.savefig('improvement_heatmap.pdf', bbox_inches='tight')
    print("Generated: improvement_heatmap.png/pdf")
    plt.close()

def main():
    """Generate all performance comparison figures."""
    print("Generating performance comparison figures...")
    
    # Change to figures directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    generate_f1_comparison_by_model()
    generate_f1_comparison_by_dataset()
    generate_metrics_comparison()
    generate_improvement_heatmap()
    
    print("\nAll performance comparison figures generated successfully!")
    print("Output files:")
    print("  - f1_comparison_by_model.png/pdf")
    print("  - f1_comparison_by_dataset.png/pdf")
    print("  - metrics_comparison_llava15_coco.png/pdf")
    print("  - improvement_heatmap.png/pdf")

if __name__ == '__main__':
    main()

