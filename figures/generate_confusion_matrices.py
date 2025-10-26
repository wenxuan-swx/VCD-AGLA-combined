#!/usr/bin/env python3
"""
Generate confusion matrix heatmaps for VCD+AGLA paper.
Shows error distribution for Baseline vs Combined method.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Set publication-quality parameters
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

# Load data
data_path = '../combined_results/comprehensive_results.json'
with open(data_path, 'r') as f:
    data = json.load(f)

def compute_confusion_matrix(accuracy, precision, recall, total):
    """
    Compute confusion matrix from metrics.
    
    For binary classification with balanced dataset (total/2 positive, total/2 negative):
    - TP = recall * (total/2)
    - FP = TP/precision - TP
    - FN = (total/2) - TP
    - TN = total - TP - FP - FN
    """
    n_positive = total / 2
    n_negative = total / 2
    
    # Calculate TP from recall
    TP = recall / 100 * n_positive
    
    # Calculate FP from precision
    if precision > 0:
        FP = TP / (precision / 100) - TP
    else:
        FP = 0
    
    # Calculate FN
    FN = n_positive - TP
    
    # Calculate TN
    TN = n_negative - FP
    
    # Round to integers
    TP, FP, FN, TN = int(round(TP)), int(round(FP)), int(round(FN)), int(round(TN))
    
    return np.array([[TP, FN], [FP, TN]])

def plot_confusion_matrix(cm, title, filename):
    """Plot a single confusion matrix."""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Normalize for color intensity
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Plot heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                cbar=True, square=True, ax=ax,
                xticklabels=['Predicted Positive', 'Predicted Negative'],
                yticklabels=['Actual Positive', 'Actual Negative'])
    
    # Add percentage annotations
    for i in range(2):
        for j in range(2):
            percentage = cm_normalized[i, j] * 100
            ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)', 
                   ha='center', va='center', fontsize=9, color='gray')
    
    ax.set_title(title)
    ax.set_ylabel('True Label')
    ax.set_xlabel('Predicted Label')
    
    plt.tight_layout()
    plt.savefig(f'{filename}.png', bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"Generated: {filename}.png/pdf")
    plt.close()

def plot_confusion_comparison(cm_baseline, cm_combined, model_name, dataset_name, filename):
    """Plot side-by-side confusion matrices for comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    for idx, (cm, method, ax) in enumerate(zip([cm_baseline, cm_combined], 
                                                 ['Baseline', 'VCD+AGLA'], 
                                                 axes)):
        # Normalize for color intensity
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Plot heatmap
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    cbar=True, square=True, ax=ax,
                    xticklabels=['Pred Pos', 'Pred Neg'],
                    yticklabels=['True Pos', 'True Neg'])
        
        # Add percentage annotations
        for i in range(2):
            for j in range(2):
                percentage = cm_normalized[i, j] * 100
                ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)', 
                       ha='center', va='center', fontsize=8, color='gray')
        
        ax.set_title(f'{method}')
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
    
    fig.suptitle(f'Confusion Matrix Comparison: {model_name} on {dataset_name}', 
                 fontsize=13, y=1.02)
    
    plt.tight_layout()
    plt.savefig(f'{filename}.png', bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"Generated: {filename}.png/pdf")
    plt.close()

def plot_error_reduction(cm_baseline, cm_combined, model_name, dataset_name, filename):
    """Plot error reduction visualization."""
    # Extract errors
    baseline_fp = cm_baseline[1, 0]
    baseline_fn = cm_baseline[0, 1]
    combined_fp = cm_combined[1, 0]
    combined_fn = cm_combined[0, 1]
    
    # Calculate reductions
    fp_reduction = (baseline_fp - combined_fp) / baseline_fp * 100 if baseline_fp > 0 else 0
    fn_reduction = (baseline_fn - combined_fn) / baseline_fn * 100 if baseline_fn > 0 else 0
    total_errors_baseline = baseline_fp + baseline_fn
    total_errors_combined = combined_fp + combined_fn
    total_reduction = (total_errors_baseline - total_errors_combined) / total_errors_baseline * 100
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Left plot: Error counts
    ax1 = axes[0]
    error_types = ['False Positives', 'False Negatives', 'Total Errors']
    baseline_errors = [baseline_fp, baseline_fn, total_errors_baseline]
    combined_errors = [combined_fp, combined_fn, total_errors_combined]
    
    x = np.arange(len(error_types))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, baseline_errors, width, label='Baseline', 
                    color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, combined_errors, width, label='VCD+AGLA', 
                    color='#27ae60', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
    
    ax1.set_xlabel('Error Type')
    ax1.set_ylabel('Count')
    ax1.set_title('Error Counts Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(error_types)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Right plot: Error reduction percentages
    ax2 = axes[1]
    reductions = [fp_reduction, fn_reduction, total_reduction]
    colors = ['#3498db', '#9b59b6', '#e67e22']
    
    bars = ax2.bar(error_types, reductions, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, reduction in zip(bars, reductions):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{reduction:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax2.set_xlabel('Error Type')
    ax2.set_ylabel('Reduction (%)')
    ax2.set_title('Error Reduction by VCD+AGLA')
    ax2.set_xticklabels(error_types, rotation=15, ha='right')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim([0, max(reductions) * 1.2])
    
    fig.suptitle(f'{model_name} on {dataset_name}', fontsize=13, y=1.02)
    
    plt.tight_layout()
    plt.savefig(f'{filename}.png', bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', bbox_inches='tight')
    print(f"Generated: {filename}.png/pdf")
    plt.close()

def plot_confusion_comparison_multi_pope(model_key='llava15'):
    """Plot confusion matrices for both POPE subsets (COCO and A-OKVQA) in 1x2 layout."""
    model_name = 'LLaVA-1.5-7B'
    datasets = [
        ('coco_pope', 'COCO'),
        ('aokvqa_pope', 'A-OKVQA')
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for idx, (dataset_key, dataset_short_name) in enumerate(datasets):
        # Get data
        baseline_metrics = data[model_key][dataset_key]['baseline']
        combined_metrics = data[model_key][dataset_key]['combined']

        # Compute confusion matrices
        cm_baseline = compute_confusion_matrix(
            baseline_metrics['accuracy'],
            baseline_metrics['precision'],
            baseline_metrics['recall'],
            baseline_metrics['total']
        )

        cm_combined = compute_confusion_matrix(
            combined_metrics['accuracy'],
            combined_metrics['precision'],
            combined_metrics['recall'],
            combined_metrics['total']
        )

        # Create subplot with 2 heatmaps side by side
        ax = axes[idx]

        # We need to create a nested subplot for each dataset
        # This is a bit tricky - we'll use a different approach
        # Just show the combined method for each dataset
        cm = cm_combined
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    cbar=True, square=True, ax=ax,
                    xticklabels=['Pred Pos', 'Pred Neg'],
                    yticklabels=['True Pos', 'True Neg'])

        # Add percentage annotations
        for i in range(2):
            for j in range(2):
                percentage = cm_normalized[i, j] * 100
                ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)',
                       ha='center', va='center', fontsize=8, color='gray')

        ax.set_title(f'{dataset_short_name} (VCD+AGLA)')
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')

    fig.suptitle(f'Confusion Matrix Comparison: {model_name} on POPE',
                 fontsize=13, y=1.02)

    plt.tight_layout()
    plt.savefig('confusion_matrix_comparison_pope.png', bbox_inches='tight')
    plt.savefig('confusion_matrix_comparison_pope.pdf', bbox_inches='tight')
    print("Generated: confusion_matrix_comparison_pope.png/pdf")
    plt.close()

def plot_error_reduction_multi_pope(model_key='llava15'):
    """Plot error reduction for both POPE subsets in 1x2 layout."""
    model_name = 'LLaVA-1.5-7B'
    datasets = [
        ('coco_pope', 'COCO'),
        ('aokvqa_pope', 'A-OKVQA')
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    for idx, (dataset_key, dataset_short_name) in enumerate(datasets):
        # Get data
        baseline_metrics = data[model_key][dataset_key]['baseline']
        combined_metrics = data[model_key][dataset_key]['combined']

        # Compute confusion matrices
        cm_baseline = compute_confusion_matrix(
            baseline_metrics['accuracy'],
            baseline_metrics['precision'],
            baseline_metrics['recall'],
            baseline_metrics['total']
        )

        cm_combined = compute_confusion_matrix(
            combined_metrics['accuracy'],
            combined_metrics['precision'],
            combined_metrics['recall'],
            combined_metrics['total']
        )

        # Extract errors
        baseline_fp = cm_baseline[1, 0]
        baseline_fn = cm_baseline[0, 1]
        combined_fp = cm_combined[1, 0]
        combined_fn = cm_combined[0, 1]

        # Calculate reductions
        fp_reduction = (baseline_fp - combined_fp) / baseline_fp * 100 if baseline_fp > 0 else 0
        fn_reduction = (baseline_fn - combined_fn) / baseline_fn * 100 if baseline_fn > 0 else 0
        total_errors_baseline = baseline_fp + baseline_fn
        total_errors_combined = combined_fp + combined_fn
        total_reduction = (total_errors_baseline - total_errors_combined) / total_errors_baseline * 100

        # Left plot: Error counts (column 0)
        ax1 = axes[idx, 0]
        error_types = ['False Positives', 'False Negatives', 'Total Errors']
        baseline_errors = [baseline_fp, baseline_fn, total_errors_baseline]
        combined_errors = [combined_fp, combined_fn, total_errors_combined]

        x = np.arange(len(error_types))
        width = 0.35

        bars1 = ax1.bar(x - width/2, baseline_errors, width, label='Baseline',
                        color='#e74c3c', alpha=0.8)
        bars2 = ax1.bar(x + width/2, combined_errors, width, label='VCD+AGLA',
                        color='#27ae60', alpha=0.8)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9)

        ax1.set_xlabel('Error Type')
        ax1.set_ylabel('Count')
        ax1.set_title(f'{dataset_short_name}: Error Counts')
        ax1.set_xticks(x)
        ax1.set_xticklabels(error_types, rotation=15, ha='right')
        if idx == 0:
            ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # Right plot: Error reduction percentages (column 1)
        ax2 = axes[idx, 1]
        reductions = [fp_reduction, fn_reduction, total_reduction]
        colors = ['#3498db', '#9b59b6', '#e67e22']

        bars = ax2.bar(error_types, reductions, color=colors, alpha=0.8)

        # Add value labels
        for bar, reduction in zip(bars, reductions):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{reduction:.1f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax2.set_xlabel('Error Type')
        ax2.set_ylabel('Reduction (%)')
        ax2.set_title(f'{dataset_short_name}: Error Reduction')
        ax2.set_xticklabels(error_types, rotation=15, ha='right')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim([min(0, min(reductions) * 1.2), max(reductions) * 1.2])

    fig.suptitle(f'{model_name} on POPE', fontsize=13, y=0.995)

    plt.tight_layout()
    plt.savefig('error_reduction_pope.png', bbox_inches='tight')
    plt.savefig('error_reduction_pope.pdf', bbox_inches='tight')
    print("Generated: error_reduction_pope.png/pdf")
    plt.close()

def main():
    """Generate all confusion matrix figures."""
    print("Generating confusion matrix figures...")

    # Change to figures directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Generate expanded POPE figures (both subsets)
    plot_confusion_comparison_multi_pope()
    plot_error_reduction_multi_pope()

    # Keep old single-subset versions for backward compatibility
    model_key = 'llava15'
    dataset_key = 'coco_pope'
    model_name = 'LLaVA-1.5-7B'
    dataset_name = 'COCO-POPE'

    baseline_metrics = data[model_key][dataset_key]['baseline']
    combined_metrics = data[model_key][dataset_key]['combined']

    cm_baseline = compute_confusion_matrix(
        baseline_metrics['accuracy'],
        baseline_metrics['precision'],
        baseline_metrics['recall'],
        baseline_metrics['total']
    )

    cm_combined = compute_confusion_matrix(
        combined_metrics['accuracy'],
        combined_metrics['precision'],
        combined_metrics['recall'],
        combined_metrics['total']
    )

    # Generate comparison plot (single subset - COCO only)
    plot_confusion_comparison(cm_baseline, cm_combined,
                            model_name, dataset_name,
                            'confusion_matrix_comparison_llava15_coco')

    # Generate error reduction plot (single subset - COCO only)
    plot_error_reduction(cm_baseline, cm_combined,
                        model_name, dataset_name,
                        'error_reduction_llava15_coco')

    print("\nAll confusion matrix figures generated successfully!")
    print("Output files:")
    print("  - confusion_matrix_comparison_pope.png/pdf (NEW: both POPE subsets)")
    print("  - error_reduction_pope.png/pdf (NEW: both POPE subsets)")
    print("  - confusion_matrix_comparison_llava15_coco.png/pdf (old single-subset)")
    print("  - error_reduction_llava15_coco.png/pdf (old single-subset)")

if __name__ == '__main__':
    main()

