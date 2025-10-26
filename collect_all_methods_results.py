#!/usr/bin/env python3
"""
Collect results from all methods (Baseline, VCD Only, AGLA Only, VCD+AGLA) 
for all models and datasets including Hallucinogen.
"""

import json
import os
from pathlib import Path

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def collect_vcd_hallucinogen_results():
    """Collect VCD Hallucinogen results."""
    vcd_dir = Path("/root/autodl-tmp/VCD/experiments/output/hallucinogen")
    
    results = {}
    models = ['llava15', 'llava16', 'qwenvl']
    tasks = ['identification', 'localization', 'visual_context', 'counterfactual']
    
    for model in models:
        results[model] = {}
        for task in tasks:
            baseline_file = vcd_dir / f"{model}_hallucinogen_{task}_baseline_metrics.json"
            vcd_file = vcd_dir / f"{model}_hallucinogen_{task}_vcd_metrics.json"
            
            if baseline_file.exists() and vcd_file.exists():
                baseline_data = load_json(baseline_file)['overall']
                vcd_data = load_json(vcd_file)['overall']
                
                results[model][f'hallucinogen_{task}'] = {
                    'baseline': {
                        'accuracy': baseline_data['accuracy'] * 100,
                        'precision': baseline_data['precision'] * 100,
                        'recall': baseline_data['recall'] * 100,
                        'f1': baseline_data['f1'] * 100,
                        'yes_proportion': baseline_data['yes_proportion'] * 100
                    },
                    'vcd_only': {
                        'accuracy': vcd_data['accuracy'] * 100,
                        'precision': vcd_data['precision'] * 100,
                        'recall': vcd_data['recall'] * 100,
                        'f1': vcd_data['f1'] * 100,
                        'yes_proportion': vcd_data['yes_proportion'] * 100
                    }
                }
    
    return results

def collect_agla_hallucinogen_results():
    """Collect AGLA Hallucinogen results from comprehensive report."""
    # Data from AGLA/output/comprehensive_agla_comparison_report.md
    
    results = {
        'llava15': {
            'hallucinogen_identification': {
                'baseline': {'accuracy': 81.33, 'precision': 90.83, 'recall': 70.78, 'f1': 79.56},
                'agla_only': {'accuracy': 83.67, 'precision': 94.87, 'recall': 72.08, 'f1': 81.92}
            },
            'hallucinogen_localization': {
                'baseline': {'accuracy': 82.00, 'precision': 87.22, 'recall': 75.82, 'f1': 81.12},
                'agla_only': {'accuracy': 84.33, 'precision': 92.74, 'recall': 75.16, 'f1': 83.03}
            },
            'hallucinogen_visual_context': {
                'baseline': {'accuracy': 81.33, 'precision': 92.62, 'recall': 70.63, 'f1': 80.14},
                'agla_only': {'accuracy': 84.67, 'precision': 95.24, 'recall': 75.00, 'f1': 83.92}
            },
            'hallucinogen_counterfactual': {
                'baseline': {'accuracy': 82.67, 'precision': 88.70, 'recall': 72.34, 'f1': 79.69},
                'agla_only': {'accuracy': 88.00, 'precision': 95.65, 'recall': 78.01, 'f1': 85.94}
            }
        },
        'llava16': {
            'hallucinogen_identification': {
                'baseline': {'accuracy': 76.00, 'precision': 92.71, 'recall': 57.79, 'f1': 71.20},
                'agla_only': {'accuracy': 79.00, 'precision': 98.92, 'recall': 59.74, 'f1': 74.49}
            },
            'hallucinogen_localization': {
                'baseline': {'accuracy': 74.33, 'precision': 89.58, 'recall': 56.21, 'f1': 69.08},
                'agla_only': {'accuracy': 79.00, 'precision': 97.87, 'recall': 60.13, 'f1': 74.49}
            },
            'hallucinogen_visual_context': {
                'baseline': {'accuracy': 77.00, 'precision': 93.33, 'recall': 61.25, 'f1': 73.96},
                'agla_only': {'accuracy': 79.33, 'precision': 100.00, 'recall': 61.25, 'f1': 75.97}
            },
            'hallucinogen_counterfactual': {
                'baseline': {'accuracy': 80.67, 'precision': 93.68, 'recall': 63.12, 'f1': 75.42},
                'agla_only': {'accuracy': 84.33, 'precision': 100.00, 'recall': 66.67, 'f1': 80.00}
            }
        },
        'qwenvl': {
            'hallucinogen_identification': {
                'baseline': {'accuracy': 82.00, 'precision': 94.64, 'recall': 68.83, 'f1': 79.70},
                'agla_only': {'accuracy': 83.67, 'precision': 96.46, 'recall': 70.78, 'f1': 81.65}
            },
            'hallucinogen_localization': {
                'baseline': {'accuracy': 82.67, 'precision': 94.69, 'recall': 69.93, 'f1': 80.45},
                'agla_only': {'accuracy': 84.00, 'precision': 96.46, 'recall': 71.24, 'f1': 81.95}
            },
            'hallucinogen_visual_context': {
                'baseline': {'accuracy': 84.33, 'precision': 95.20, 'recall': 74.38, 'f1': 83.51},
                'agla_only': {'accuracy': 85.33, 'precision': 96.03, 'recall': 75.62, 'f1': 84.62}
            },
            'hallucinogen_counterfactual': {
                'baseline': {'accuracy': 88.00, 'precision': 97.30, 'recall': 76.60, 'f1': 85.71},
                'agla_only': {'accuracy': 88.00, 'precision': 99.07, 'recall': 75.18, 'f1': 85.48}
            }
        }
    }
    
    return results

def collect_combined_results():
    """Collect VCD+AGLA combined results."""
    combined_file = Path("/root/autodl-tmp/COMBINED/combined_results/comprehensive_results.json")
    data = load_json(combined_file)
    
    results = {}
    for model_key, datasets in data.items():
        results[model_key] = {}
        for dataset_key, methods in datasets.items():
            if 'combined' in methods:
                results[model_key][dataset_key] = {
                    'combined': methods['combined']
                }
    
    return results

def merge_all_results():
    """Merge all results from different sources."""
    print("Collecting VCD Hallucinogen results...")
    vcd_results = collect_vcd_hallucinogen_results()
    
    print("Collecting AGLA Hallucinogen results...")
    agla_results = collect_agla_hallucinogen_results()
    
    print("Collecting Combined results...")
    combined_results = collect_combined_results()
    
    # Merge everything
    all_results = {}
    
    for model in ['llava15', 'llava16', 'qwenvl']:
        all_results[model] = {}
        
        # Hallucinogen datasets
        for task in ['identification', 'localization', 'visual_context', 'counterfactual']:
            dataset_key = f'hallucinogen_{task}'
            
            all_results[model][dataset_key] = {}
            
            # Baseline and VCD from VCD results
            if model in vcd_results and dataset_key in vcd_results[model]:
                all_results[model][dataset_key]['baseline'] = vcd_results[model][dataset_key]['baseline']
                all_results[model][dataset_key]['vcd_only'] = vcd_results[model][dataset_key]['vcd_only']
            
            # AGLA from AGLA results
            if model in agla_results and dataset_key in agla_results[model]:
                all_results[model][dataset_key]['agla_only'] = agla_results[model][dataset_key]['agla_only']
            
            # Combined from combined results
            if model in combined_results and dataset_key in combined_results[model]:
                all_results[model][dataset_key]['combined'] = combined_results[model][dataset_key]['combined']
    
    return all_results

def print_latex_table(results):
    """Print LaTeX table for Hallucinogen results."""
    print("\n" + "="*80)
    print("LaTeX Table for Hallucinogen Results (Table 2)")
    print("="*80 + "\n")
    
    models = [
        ('llava15', 'LLaVA-1.5'),
        ('llava16', 'LLaVA-1.6'),
        ('qwenvl', 'Qwen-VL')
    ]
    
    tasks = [
        ('hallucinogen_identification', 'Identification'),
        ('hallucinogen_localization', 'Localization'),
        ('hallucinogen_visual_context', 'Visual Context'),
        ('hallucinogen_counterfactual', 'Counterfactual')
    ]
    
    print("\\begin{table*}[t]")
    print("\\centering")
    print("\\caption{Results on Hallucinogen benchmark (300 samples per task). VCD+AGLA consistently outperforms individual methods.}")
    print("\\label{tab:hallucinogen}")
    print("\\begin{tabular}{llcccc}")
    print("\\toprule")
    print("\\textbf{Model} & \\textbf{Method} & \\textbf{Accuracy} & \\textbf{Precision} & \\textbf{Recall} & \\textbf{F1} \\\\")
    print("\\midrule")
    
    for task_key, task_name in tasks:
        print(f"\\multicolumn{{6}}{{l}}{{\\textit{{{task_name}}}}} \\\\")
        
        for model_key, model_name in models:
            if model_key in results and task_key in results[model_key]:
                data = results[model_key][task_key]
                
                # Baseline
                if 'baseline' in data:
                    b = data['baseline']
                    print(f"{model_name} & Baseline & {b['accuracy']:.2f} & {b['precision']:.2f} & {b['recall']:.2f} & {b['f1']:.2f} \\\\")
                
                # VCD Only
                if 'vcd_only' in data:
                    v = data['vcd_only']
                    print(f" & VCD Only & {v['accuracy']:.2f} & {v['precision']:.2f} & {v['recall']:.2f} & {v['f1']:.2f} \\\\")
                
                # AGLA Only
                if 'agla_only' in data:
                    a = data['agla_only']
                    print(f" & AGLA Only & {a['accuracy']:.2f} & {a['precision']:.2f} & {a['recall']:.2f} & {a['f1']:.2f} \\\\")
                
                # Combined
                if 'combined' in data:
                    c = data['combined']
                    print(f" & VCD+AGLA & {c['accuracy']:.2f} & {c['precision']:.2f} & {c['recall']:.2f} & {c['f1']:.2f} \\\\")
        
        if task_key != 'hallucinogen_counterfactual':
            print("\\midrule")
    
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table*}")

def main():
    print("Collecting all experimental results...")
    results = merge_all_results()
    
    # Save to JSON
    output_file = Path("/root/autodl-tmp/COMBINED/all_methods_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved complete results to: {output_file}")
    
    # Print LaTeX table
    print_latex_table(results)
    
    # Print summary
    print("\n" + "="*80)
    print("Summary Statistics")
    print("="*80)
    
    for model_key in ['llava15', 'llava16', 'qwenvl']:
        if model_key in results:
            print(f"\n{model_key.upper()}:")
            for dataset_key in results[model_key]:
                print(f"  {dataset_key}:")
                for method in ['baseline', 'vcd_only', 'agla_only', 'combined']:
                    if method in results[model_key][dataset_key]:
                        f1 = results[model_key][dataset_key][method]['f1']
                        print(f"    {method:12s}: F1 = {f1:.2f}")

if __name__ == "__main__":
    main()

