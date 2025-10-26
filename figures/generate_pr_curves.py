#!/usr/bin/env python3
"""
Generate precision-recall curves for VCD+AGLA paper.
Shows precision-recall trade-offs for different methods.
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
plt.rcParams['legend.fontsize'] = 9

# Load data
data_path = '../combined_results/comprehensive_results.json'
with open(data_path, 'r') as f:
    data = json.load(f)

def plot_pr_scatter():
    """Plot precision-recall scatter plot for all methods and models."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    datasets = [('coco_pope', 'COCO-POPE'), ('aokvqa_pope', 'AOKVQA-POPE')]
    
    for idx, (dataset_key, dataset_name) in enumerate(datasets):
        ax = axes[idx]
        
        # Colors and markers for different models
        model_colors = {'llava15': '#e74c3c', 'llava16': '#3498db', 'qwenvl': '#2ecc71'}
        model_names = {'llava15': 'LLaVA-1.5', 'llava16': 'LLaVA-1.6', 'qwenvl': 'Qwen-VL'}
        
        # Plot baseline points
        for model_key, color in model_colors.items():
            if dataset_key in data[model_key]:
                baseline = data[model_key][dataset_key]['baseline']
                ax.scatter(baseline['recall'], baseline['precision'], 
                          s=100, c=color, marker='o', alpha=0.6,
                          label=f"{model_names[model_key]} Baseline")
        
        # Plot combined points
        for model_key, color in model_colors.items():
            if dataset_key in data[model_key]:
                combined = data[model_key][dataset_key]['combined']
                ax.scatter(combined['recall'], combined['precision'], 
                          s=100, c=color, marker='*', alpha=0.9,
                          label=f"{model_names[model_key]} VCD+AGLA")
        
        # Draw arrows showing improvement
        for model_key, color in model_colors.items():
            if dataset_key in data[model_key]:
                baseline = data[model_key][dataset_key]['baseline']
                combined = data[model_key][dataset_key]['combined']
                ax.annotate('', xy=(combined['recall'], combined['precision']),
                           xytext=(baseline['recall'], baseline['precision']),
                           arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=0.5))
        
        # Add F1 iso-curves
        recall_range = np.linspace(50, 100, 100)
        for f1 in [70, 75, 80, 85, 90]:
            precision_curve = f1 * recall_range / (2 * recall_range - f1)
            # Only plot valid range
            valid_idx = (precision_curve >= 50) & (precision_curve <= 100)
            ax.plot(recall_range[valid_idx], precision_curve[valid_idx], 
                   'k--', alpha=0.2, linewidth=0.5)
            # Add F1 label
            if np.any(valid_idx):
                mid_idx = np.where(valid_idx)[0][len(np.where(valid_idx)[0])//2]
                ax.text(recall_range[mid_idx], precision_curve[mid_idx], 
                       f'F1={f1}', fontsize=7, alpha=0.4, rotation=-45)
        
        ax.set_xlabel('Recall (%)')
        ax.set_ylabel('Precision (%)')
        ax.set_title(dataset_name)
        ax.legend(loc='lower left', fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([55, 90])
        ax.set_ylim([75, 102])
    
    plt.tight_layout()
    plt.savefig('pr_scatter_comparison.png', bbox_inches='tight')
    plt.savefig('pr_scatter_comparison.pdf', bbox_inches='tight')
    print("Generated: pr_scatter_comparison.png/pdf")
    plt.close()

def plot_pr_improvement_vectors():
    """Plot precision-recall improvement as vectors for LLaVA-1.5."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    model_key = 'llava15'
    datasets = {
        'coco_pope': 'COCO-POPE',
        'aokvqa_pope': 'AOKVQA-POPE',
        'hallucinogen_identification': 'Hallucinogen-ID',
        'hallucinogen_localization': 'Hallucinogen-Loc',
        'hallucinogen_visual_context': 'Hallucinogen-VC',
        'hallucinogen_counterfactual': 'Hallucinogen-CF'
    }
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(datasets)))
    
    for idx, (dataset_key, dataset_name) in enumerate(datasets.items()):
        if dataset_key in data[model_key]:
            baseline = data[model_key][dataset_key]['baseline']
            combined = data[model_key][dataset_key]['combined']
            
            # Plot baseline point
            ax.scatter(baseline['recall'], baseline['precision'], 
                      s=80, c=[colors[idx]], marker='o', alpha=0.6)
            
            # Plot combined point
            ax.scatter(combined['recall'], combined['precision'], 
                      s=120, c=[colors[idx]], marker='*', alpha=0.9,
                      label=dataset_name)
            
            # Draw arrow
            ax.annotate('', xy=(combined['recall'], combined['precision']),
                       xytext=(baseline['recall'], baseline['precision']),
                       arrowprops=dict(arrowstyle='->', color=colors[idx], lw=2, alpha=0.7))
    
    ax.set_xlabel('Recall (%)')
    ax.set_ylabel('Precision (%)')
    ax.set_title('Precision-Recall Improvement: LLaVA-1.5-7B\n(Baseline → VCD+AGLA)')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pr_improvement_vectors_llava15.png', bbox_inches='tight')
    plt.savefig('pr_improvement_vectors_llava15.pdf', bbox_inches='tight')
    print("Generated: pr_improvement_vectors_llava15.png/pdf")
    plt.close()

def plot_precision_recall_bars():
    """Plot precision and recall as grouped bar charts."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    models = {
        'llava15': 'LLaVA-1.5-7B',
        'llava16': 'LLaVA-1.6-7B',
        'qwenvl': 'Qwen-VL'
    }
    
    datasets = {
        'coco_pope': 'COCO-POPE',
        'aokvqa_pope': 'AOKVQA-POPE'
    }
    
    plot_idx = 0
    for model_key, model_name in models.items():
        for dataset_key, dataset_name in datasets.items():
            ax = axes[plot_idx]
            
            baseline = data[model_key][dataset_key]['baseline']
            combined = data[model_key][dataset_key]['combined']
            
            metrics = ['Precision', 'Recall']
            baseline_values = [baseline['precision'], baseline['recall']]
            combined_values = [combined['precision'], combined['recall']]
            
            x = np.arange(len(metrics))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, baseline_values, width, 
                          label='Baseline', color='#3498db', alpha=0.8)
            bars2 = ax.bar(x + width/2, combined_values, width, 
                          label='VCD+AGLA', color='#e74c3c', alpha=0.8)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}',
                           ha='center', va='bottom', fontsize=8)
            
            ax.set_ylabel('Score (%)')
            ax.set_title(f'{model_name}\n{dataset_name}')
            ax.set_xticks(x)
            ax.set_xticklabels(metrics)
            ax.legend(fontsize=8)
            ax.grid(axis='y', alpha=0.3)
            ax.set_ylim([0, 105])
            
            plot_idx += 1
    
    plt.tight_layout()
    plt.savefig('precision_recall_bars.png', bbox_inches='tight')
    plt.savefig('precision_recall_bars.pdf', bbox_inches='tight')
    print("Generated: precision_recall_bars.png/pdf")
    plt.close()

def main():
    """Generate all precision-recall figures."""
    print("Generating precision-recall figures...")
    
    # Change to figures directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    plot_pr_scatter()
    plot_pr_improvement_vectors()
    plot_precision_recall_bars()
    
    print("\nAll precision-recall figures generated successfully!")
    print("Output files:")
    print("  - pr_scatter_comparison.png/pdf")
    print("  - pr_improvement_vectors_llava15.png/pdf")
    print("  - precision_recall_bars.png/pdf")

if __name__ == '__main__':
    main()

