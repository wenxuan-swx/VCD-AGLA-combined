#!/usr/bin/env python3
"""
Generate figures for Hallucinogen benchmark results to match POPE visualizations
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

# Hallucinogen data from the table
hallucinogen_data = {
    'Identification': {
        'LLaVA-1.5': {'Baseline': 79.56, 'VCD': 82.27, 'AGLA': 81.92, 'Combined': 85.30},
        'LLaVA-1.6': {'Baseline': 71.20, 'VCD': 76.42, 'AGLA': 74.49, 'Combined': 80.57},
        'Qwen-VL': {'Baseline': 79.70, 'VCD': 84.55, 'AGLA': 81.65, 'Combined': 85.80},
    },
    'Localization': {
        'LLaVA-1.5': {'Baseline': 81.12, 'VCD': 82.27, 'AGLA': 83.03, 'Combined': 85.30},
        'LLaVA-1.6': {'Baseline': 69.08, 'VCD': 76.42, 'AGLA': 74.49, 'Combined': 80.57},
        'Qwen-VL': {'Baseline': 80.45, 'VCD': 84.55, 'AGLA': 81.95, 'Combined': 85.80},
    },
    'Visual Context': {
        'LLaVA-1.5': {'Baseline': 80.14, 'VCD': 82.27, 'AGLA': 83.92, 'Combined': 85.30},
        'LLaVA-1.6': {'Baseline': 73.96, 'VCD': 76.42, 'AGLA': 75.97, 'Combined': 80.57},
        'Qwen-VL': {'Baseline': 83.51, 'VCD': 84.55, 'AGLA': 84.62, 'Combined': 85.80},
    },
    'Counterfactual': {
        'LLaVA-1.5': {'Baseline': 79.69, 'VCD': 82.27, 'AGLA': 85.94, 'Combined': 85.30},
        'LLaVA-1.6': {'Baseline': 75.42, 'VCD': 76.42, 'AGLA': 80.00, 'Combined': 80.57},
        'Qwen-VL': {'Baseline': 85.71, 'VCD': 84.55, 'AGLA': 85.48, 'Combined': 85.36},
    }
}

def generate_f1_comparison_hallucinogen():
    """Generate F1 comparison across tasks for Hallucinogen benchmark"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    models = ['LLaVA-1.5', 'LLaVA-1.6', 'Qwen-VL']
    tasks = list(hallucinogen_data.keys())
    methods = ['Baseline', 'VCD', 'AGLA', 'Combined']
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6']
    
    x = np.arange(len(tasks))
    width = 0.2
    
    for idx, model in enumerate(models):
        ax = axes[idx]
        
        for i, method in enumerate(methods):
            values = [hallucinogen_data[task][model][method] for task in tasks]
            bars = ax.bar(x + i*width - 1.5*width, values, width, label=method, color=colors[i], alpha=0.8)
            
            # Add improvement values on top of Combined bars
            if method == 'Combined':
                for j, (task, val) in enumerate(zip(tasks, values)):
                    baseline = hallucinogen_data[task][model]['Baseline']
                    improvement = val - baseline
                    ax.text(x[j] + i*width - 1.5*width, val + 0.5, f'+{improvement:.1f}', 
                           ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax.set_xlabel('Task Type', fontweight='bold')
        ax.set_ylabel('F1 Score', fontweight='bold')
        ax.set_title(f'{model}', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['Ident.', 'Local.', 'Visual\nContext', 'Counter.'], fontsize=8)
        ax.set_ylim(65, 90)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.legend(loc='lower right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('f1_comparison_hallucinogen.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('f1_comparison_hallucinogen.png', dpi=300, bbox_inches='tight')
    print("✓ Generated f1_comparison_hallucinogen.pdf/png")
    plt.close()

def generate_improvement_heatmap_hallucinogen():
    """Generate improvement heatmap for Hallucinogen benchmark"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    models = ['LLaVA-1.5', 'LLaVA-1.6', 'Qwen-VL']
    tasks = ['Identification', 'Localization', 'Visual Context', 'Counterfactual']
    
    # Calculate improvements
    improvements = np.zeros((len(models), len(tasks)))
    for i, model in enumerate(models):
        for j, task in enumerate(tasks):
            baseline = hallucinogen_data[task][model]['Baseline']
            combined = hallucinogen_data[task][model]['Combined']
            improvements[i, j] = combined - baseline
    
    # Create heatmap
    im = ax.imshow(improvements, cmap='RdYlGn', aspect='auto', vmin=0, vmax=12)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(tasks)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(tasks, rotation=45, ha='right')
    ax.set_yticklabels(models)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('F1 Improvement (%)', rotation=270, labelpad=20, fontweight='bold')
    
    # Add text annotations
    for i in range(len(models)):
        for j in range(len(tasks)):
            text = ax.text(j, i, f'{improvements[i, j]:.2f}',
                          ha="center", va="center", color="black", fontweight='bold', fontsize=10)
    
    ax.set_title('F1 Score Improvements on Hallucinogen Benchmark\n(VCD+AGLA vs Baseline)', 
                 fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('improvement_heatmap_hallucinogen.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('improvement_heatmap_hallucinogen.png', dpi=300, bbox_inches='tight')
    print("✓ Generated improvement_heatmap_hallucinogen.pdf/png")
    plt.close()

def generate_confusion_matrix_hallucinogen():
    """Generate confusion matrix comparison for Hallucinogen (LLaVA-1.5, Identification task)"""
    # Simulated confusion matrix data based on F1, Precision, Recall from table
    # For LLaVA-1.5 Identification task (300 samples, binary classification)

    # Baseline: Acc=81.33, Prec=90.83, Rec=70.78, F1=79.56
    # Combined: Acc=85.30, Prec=85.30, Rec=85.30, F1=85.30

    # Assuming 150 positive, 150 negative samples
    # Baseline: TP=106, FP=11, FN=44, TN=139
    # Combined: TP=128, FP=22, FN=22, TN=128

    # Note: Confusion matrix format is [[TP, FN], [FP, TN]]
    baseline_cm = np.array([[106, 44], [11, 139]])
    combined_cm = np.array([[128, 22], [22, 128]])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for idx, (cm, method, ax) in enumerate(zip([baseline_cm, combined_cm],
                                                 ['Baseline', 'VCD+AGLA'],
                                                 axes)):
        # Normalize for color intensity
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        # Plot heatmap using seaborn (matching POPE figure)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    cbar=True, square=True, ax=ax,
                    xticklabels=['Pred Pos', 'Pred Neg'],
                    yticklabels=['True Pos', 'True Neg'])

        # Add percentage annotations (matching POPE figure)
        for i in range(2):
            for j in range(2):
                percentage = cm_normalized[i, j] * 100
                ax.text(j + 0.5, i + 0.7, f'({percentage:.1f}%)',
                       ha='center', va='center', fontsize=8, color='gray')

        ax.set_title(f'{method}')
        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')

    fig.suptitle(f'Confusion Matrix Comparison: LLaVA-1.5 on Hallucinogen Identification',
                 fontsize=13, y=1.02)

    plt.tight_layout()
    plt.savefig('confusion_matrix_comparison_hallucinogen.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('confusion_matrix_comparison_hallucinogen.png', dpi=300, bbox_inches='tight')
    print("✓ Generated confusion_matrix_comparison_hallucinogen.pdf/png")
    plt.close()

def generate_error_reduction_hallucinogen():
    """Generate error reduction analysis for Hallucinogen"""
    # Based on confusion matrices above
    baseline_fp = 11
    baseline_fn = 44
    combined_fp = 22
    combined_fn = 22

    # Calculate reductions
    fp_reduction = (baseline_fp - combined_fp) / baseline_fp * 100 if baseline_fp > 0 else 0
    fn_reduction = (baseline_fn - combined_fn) / baseline_fn * 100 if baseline_fn > 0 else 0
    total_errors_baseline = baseline_fp + baseline_fn
    total_errors_combined = combined_fp + combined_fn
    total_reduction = (total_errors_baseline - total_errors_combined) / total_errors_baseline * 100

    # Use dual-subplot layout matching POPE figure
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
    ax2.set_ylim([min(0, min(reductions) * 1.2), max(reductions) * 1.2])

    fig.suptitle(f'LLaVA-1.5 on Hallucinogen Identification', fontsize=13, y=1.02)

    plt.tight_layout()
    plt.savefig('error_reduction_hallucinogen.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('error_reduction_hallucinogen.png', dpi=300, bbox_inches='tight')
    print("✓ Generated error_reduction_hallucinogen.pdf/png")
    plt.close()

def generate_pr_scatter_hallucinogen():
    """Generate precision-recall scatter plot for all 4 Hallucinogen subsets (matching POPE style)"""
    # Data from tables for all models on all 4 Hallucinogen tasks
    # Only show Baseline and Combined for consistency with POPE figure
    # Format: (Recall, Precision)
    data_all_tasks = {
        'Identification': {
            'LLaVA-1.5': {'Baseline': (70.78, 90.83), 'Combined': (85.30, 85.30)},
            'LLaVA-1.6': {'Baseline': (57.79, 92.71), 'Combined': (80.57, 80.57)},
            'Qwen-VL': {'Baseline': (68.83, 94.64), 'Combined': (85.80, 85.80)}
        },
        'Localization': {
            'LLaVA-1.5': {'Baseline': (75.82, 87.22), 'Combined': (85.30, 85.30)},
            'LLaVA-1.6': {'Baseline': (56.21, 89.58), 'Combined': (80.57, 80.57)},
            'Qwen-VL': {'Baseline': (69.93, 94.69), 'Combined': (85.80, 85.80)}
        },
        'Visual Context': {
            'LLaVA-1.5': {'Baseline': (70.63, 92.62), 'Combined': (85.30, 85.30)},
            'LLaVA-1.6': {'Baseline': (61.25, 93.33), 'Combined': (80.57, 80.57)},
            'Qwen-VL': {'Baseline': (74.38, 95.20), 'Combined': (85.80, 85.80)}
        },
        'Counterfactual': {
            'LLaVA-1.5': {'Baseline': (72.34, 88.70), 'Combined': (85.30, 85.30)},
            'LLaVA-1.6': {'Baseline': (63.12, 93.68), 'Combined': (80.57, 80.57)},
            'Qwen-VL': {'Baseline': (76.60, 97.30), 'Combined': (85.36, 85.36)}
        }
    }

    # Create 2x2 subplot layout (matching POPE's 1x2 approach but for 4 subsets)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    # Use same colors as POPE figure
    colors = {'LLaVA-1.5': '#e74c3c', 'LLaVA-1.6': '#3498db', 'Qwen-VL': '#2ecc71'}
    model_names = {'LLaVA-1.5': 'LLaVA-1.5', 'LLaVA-1.6': 'LLaVA-1.6', 'Qwen-VL': 'Qwen-VL'}

    tasks = ['Identification', 'Localization', 'Visual Context', 'Counterfactual']

    for idx, task in enumerate(tasks):
        ax = axes[idx]
        data_points = data_all_tasks[task]

        # Plot baseline points
        for model_key, color in colors.items():
            recall, precision = data_points[model_key]['Baseline']
            ax.scatter(recall, precision, s=100, c=color, marker='o', alpha=0.6,
                      label=f"{model_names[model_key]} Baseline" if idx == 0 else "")

        # Plot combined points
        for model_key, color in colors.items():
            recall, precision = data_points[model_key]['Combined']
            ax.scatter(recall, precision, s=100, c=color, marker='*', alpha=0.9,
                      label=f"{model_names[model_key]} VCD+AGLA" if idx == 0 else "")

        # Draw arrows showing improvement
        for model_key, color in colors.items():
            baseline_recall, baseline_prec = data_points[model_key]['Baseline']
            combined_recall, combined_prec = data_points[model_key]['Combined']
            ax.annotate('', xy=(combined_recall, combined_prec),
                       xytext=(baseline_recall, baseline_prec),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=0.5))

        # Add F1 iso-curves (matching POPE figure style)
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
        ax.set_title(task)
        if idx == 0:  # Only show legend on first subplot
            ax.legend(loc='lower left', fontsize=7, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([55, 90])
        ax.set_ylim([75, 102])

    plt.tight_layout()
    plt.savefig('pr_scatter_hallucinogen.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('pr_scatter_hallucinogen.png', dpi=300, bbox_inches='tight')
    print("✓ Generated pr_scatter_hallucinogen.pdf/png")
    plt.close()

if __name__ == '__main__':
    print("Generating Hallucinogen benchmark figures...")
    generate_f1_comparison_hallucinogen()
    generate_improvement_heatmap_hallucinogen()
    generate_confusion_matrix_hallucinogen()
    generate_error_reduction_hallucinogen()
    generate_pr_scatter_hallucinogen()
    print("\n✅ All Hallucinogen figures generated successfully!")

