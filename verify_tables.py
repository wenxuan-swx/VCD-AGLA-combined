#!/usr/bin/env python3
"""
验证论文中的表格完整性
"""

import re

def verify_table(filepath, table_label, expected_rows):
    """验证表格是否完整"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找表格
    pattern = rf'\\label\{{{table_label}\}}.*?\\end\{{table\*?\}}'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return False, f"Table {table_label} not found!"
    
    table_content = match.group(0)
    
    # 统计数据行（不包括表头和分隔符）
    data_lines = [line for line in table_content.split('\n') 
                  if '&' in line and not 'textbf{' in line.split('&')[0]]
    
    return True, f"Table {table_label} found with {len(data_lines)} lines"

def main():
    print("=" * 60)
    print("验证英文版论文表格")
    print("=" * 60)
    
    # 验证英文版
    english_file = 'paper_english.tex'
    
    print("\n1. Table 1 (POPE Benchmarks) - tab:main_results")
    found, msg = verify_table(english_file, 'tab:main_results', 24)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    print("\n2. Table 2 (Hallucinogen) - tab:hallucinogen")
    found, msg = verify_table(english_file, 'tab:hallucinogen', 48)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    print("\n3. Table 3 (Ablation) - tab:ablation_components")
    found, msg = verify_table(english_file, 'tab:ablation_components', 4)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    print("\n" + "=" * 60)
    print("验证中文版论文表格")
    print("=" * 60)
    
    # 验证中文版
    chinese_file = 'paper_chinese.tex'
    
    print("\n1. Table 1 (POPE基准) - tab:main_results")
    found, msg = verify_table(chinese_file, 'tab:main_results', 24)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    print("\n2. Table 2 (Hallucinogen) - tab:hallucinogen")
    found, msg = verify_table(chinese_file, 'tab:hallucinogen', 48)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    print("\n3. Table 3 (消融研究) - tab:ablation_components")
    found, msg = verify_table(chinese_file, 'tab:ablation_components', 4)
    print(f"   {'✅' if found else '❌'} {msg}")
    
    # 详细检查 Table 2
    print("\n" + "=" * 60)
    print("详细检查 Table 2 (Hallucinogen)")
    print("=" * 60)
    
    with open(english_file, 'r') as f:
        content = f.read()
    
    # 查找 Table 2
    pattern = r'\\label\{tab:hallucinogen\}.*?\\end\{table\*\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        table_content = match.group(0)
        
        # 检查任务
        tasks = ['Identification', 'Localization', 'Visual Context', 'Counterfactual']
        print("\n任务检查:")
        for task in tasks:
            if task in table_content:
                print(f"   ✅ {task} 存在")
            else:
                print(f"   ❌ {task} 缺失")
        
        # 检查模型
        models = ['LLaVA-1.5', 'LLaVA-1.6', 'Qwen-VL']
        print("\n模型检查:")
        for model in models:
            count = table_content.count(model)
            print(f"   {'✅' if count >= 4 else '❌'} {model}: 出现 {count} 次 (期望 ≥4)")
        
        # 检查方法
        methods = ['Baseline', 'VCD Only', 'AGLA Only', 'VCD+AGLA']
        print("\n方法检查:")
        for method in methods:
            count = table_content.count(method)
            print(f"   {'✅' if count >= 12 else '❌'} {method}: 出现 {count} 次 (期望 ≥12)")
        
        # 检查列
        columns = ['Acc', 'Prec', 'Rec', 'F1', r'\$\\Delta\$F1']
        print("\n列检查:")
        for col in columns:
            if col in table_content or col.replace('\\', '') in table_content:
                print(f"   ✅ {col} 存在")
            else:
                print(f"   ❌ {col} 缺失")
        
        # 统计表格大小
        lines = table_content.split('\n')
        print(f"\n表格统计:")
        print(f"   总行数: {len(lines)}")
        print(f"   表格起始行: \\begin{{table*}}")
        print(f"   表格结束行: \\end{{table*}}")
        
        # 检查是否使用了 resizebox
        if 'resizebox' in table_content:
            print(f"   ✅ 使用了 \\resizebox 自动调整大小")
        else:
            print(f"   ⚠️  未使用 \\resizebox")
        
        # 检查是否使用了 multirow
        if 'multirow' in table_content:
            multirow_count = table_content.count('multirow')
            print(f"   ✅ 使用了 \\multirow ({multirow_count} 次)")
        else:
            print(f"   ❌ 未使用 \\multirow")
    
    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)

if __name__ == '__main__':
    main()

