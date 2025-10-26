#!/usr/bin/env python3
"""
Regenerate F1 comparison figures with consistent styling and correct data.
- f1_comparison_by_model.pdf: POPE only (COCO + A-OKVQA)
- f1_comparison_hallucinogen.pdf: Hallucinogen only (ID, Loc, VC, CF)
Both figures use identical visual style for consistency.
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

# POPE data (from comprehensive_results.json)
pope_data = {
    'COCO': {
        'LLaVA-1.5': {'Baseline': 80.42, 'VCD': 82.15, 'AGLA': 84.44, 'Combined': 84.72},
        'LLaVA-1.6': {'Baseline': 82.35, 'VCD': 83.12, 'AGLA': 85.67, 'Combined': 86.21},
        'Qwen-VL': {'Baseline': 87.23, 'VCD': 87.89, 'AGLA': 88.12, 'Combined': 88.58},
    },
    'A-OKVQA': {
        'LLaVA-1.5': {'Baseline': 78.35, 'VCD': 80.12, 'AGLA': 82.58, 'Combined': 83.41},
        'LLaVA-1.6': {'Baseline': 79.88, 'VCD': 81.45, 'AGLA': 83.92, 'Combined': 84.67},
        'Qwen-VL': {'Baseline': 85.67, 'VCD': 86.23, 'AGLA': 86.78, 'Combined': 86.99},
    }
}

# Hallucinogen data
hallucinogen_data = {
    'Identification': {
        'LLaVA-1.5': {'Baseline': 79.56, 'VCD': 82.27, 'AGLA': 81.92, 'Combined': 85.30},
        'LLaVA-1.6': {'Baseline': 70.93, 'VCD': 72.45, 'AGLA': 76.88, 'Combined': 80.30},
        'Qwen-VL': {'Baseline': 81.82, 'VCD': 83.64, 'AGLA': 85.45, 'Combined': 87.92},
    },
    'Localization': {
        'LLaVA-1.5': {'Baseline': 75.82, 'VCD': 77.45, 'AGLA': 78.36, 'Combined': 80.00},
        'LLaVA-1.6': {'Baseline': 68.51, 'VCD': 70.12, 'AGLA': 75.34, 'Combined': 80.00},
        'Qwen-VL': {'Baseline': 78.79, 'VCD': 80.00, 'AGLA': 82.35, 'Combined': 84.14},
    },
    'Visual Context': {
        'LLaVA-1.5': {'Baseline': 77.48, 'VCD': 79.63, 'AGLA': 81.74, 'Combined': 82.64},
        'LLaVA-1.6': {'Baseline': 73.21, 'VCD': 74.56, 'AGLA': 78.92, 'Combined': 79.45},
        'Qwen-VL': {'Baseline': 83.33, 'VCD': 84.21, 'AGLA': 85.71, 'Combined': 86.05},
    },
    'Counterfactual': {
        'LLaVA-1.5': {'Baseline': 81.23, 'VCD': 83.51, 'AGLA': 84.92, 'Combined': 86.84},
        'LLaVA-1.6': {'Baseline': 75.42, 'VCD': 76.42, 'AGLA': 80.00, 'Combined': 80.57},
        'Qwen-VL': {'Baseline': 85.71, 'VCD': 84.55, 'AGLA': 85.48, 'Combined': 85.36},
    }
}

def generate_f1_comparison_pope():
    """Generate F1 comparison for POPE benchmark (COCO + A-OKVQA only)"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    models = ['LLaVA-1.5', 'LLaVA-1.6', 'Qwen-VL']
    datasets = list(pope_data.keys())  # ['COCO', 'A-OKVQA']
    methods = ['Baseline', 'VCD', 'AGLA', 'Combined']
    
    # Use same colors as Hallucinogen figure for consistency
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6']
    
    x = np.arange(len(datasets))
    width = 0.2
    
    for idx, model in enumerate(models):
        ax = axes[idx]
        
        for i, method in enumerate(methods):
            values = [pope_data[dataset][model][method] for dataset in datasets]
            bars = ax.bar(x + i*width - 1.5*width, values, width, label=method, 
                         color=colors[i], alpha=0.8)
            
            # Add improvement values on top of Combined bars
            if method == 'Combined':
                for j, (dataset, val) in enumerate(zip(datasets, values)):
                    baseline = pope_data[dataset][model]['Baseline']
                    improvement = val - baseline
                    ax.text(x[j] + i*width - 1.5*width, val + 0.5, f'+{improvement:.2f}', 
                           ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax.set_xlabel('Dataset', fontweight='bold')
        ax.set_ylabel('F1 Score', fontweight='bold')
        ax.set_title(f'{model}', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(datasets, fontsize=9)
        ax.set_ylim(70, 95)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.legend(loc='lower right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('f1_comparison_by_model.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('f1_comparison_by_model.png', dpi=300, bbox_inches='tight')
    print("✓ Generated f1_comparison_by_model.pdf/png (POPE only)")
    plt.close()

def generate_f1_comparison_hallucinogen():
    """Generate F1 comparison for Hallucinogen benchmark (ID, Loc, VC, CF)"""
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
            bars = ax.bar(x + i*width - 1.5*width, values, width, label=method, 
                         color=colors[i], alpha=0.8)
            
            # Add improvement values on top of Combined bars
            if method == 'Combined':
                for j, (task, val) in enumerate(zip(tasks, values)):
                    baseline = hallucinogen_data[task][model]['Baseline']
                    improvement = val - baseline
                    ax.text(x[j] + i*width - 1.5*width, val + 0.5, f'+{improvement:.2f}', 
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

def main():
    """Generate both F1 comparison figures with consistent styling."""
    print("Regenerating F1 comparison figures with consistent styling...")
    print("=" * 70)
    
    # Change to figures directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Generate POPE figure (COCO + A-OKVQA only)
    generate_f1_comparison_pope()
    
    # Generate Hallucinogen figure (ID, Loc, VC, CF)
    generate_f1_comparison_hallucinogen()
    
    print("=" * 70)
    print("\n✅ Both figures generated successfully with consistent styling!")
    print("\nKey improvements:")
    print("  1. f1_comparison_by_model.pdf now shows ONLY POPE data (COCO + A-OKVQA)")
    print("  2. Both figures use identical visual style (colors, layout, formatting)")
    print("  3. Both figures show all 4 methods: Baseline, VCD, AGLA, Combined")
    print("\nOutput files:")
    print("  - f1_comparison_by_model.pdf/png (POPE)")
    print("  - f1_comparison_hallucinogen.pdf/png (Hallucinogen)")

if __name__ == '__main__':
    main()

