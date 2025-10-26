#!/usr/bin/env python3
"""
全面检查论文中的所有引用（图片、表格、文献）
"""

import re
import os
from pathlib import Path
from collections import defaultdict

def extract_figure_references(tex_file):
    """提取所有图片引用"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \includegraphics
    pattern = r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}'
    matches = re.findall(pattern, content)
    return matches

def extract_table_labels(tex_file):
    """提取所有表格标签"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \label{tab:...}
    pattern = r'\\label\{(tab:[^}]+)\}'
    matches = re.findall(pattern, content)
    return matches

def extract_table_refs(tex_file):
    """提取所有表格引用"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \ref{tab:...}
    pattern = r'\\ref\{(tab:[^}]+)\}'
    matches = re.findall(pattern, content)
    return matches

def extract_figure_labels(tex_file):
    """提取所有图片标签"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \label{fig:...}
    pattern = r'\\label\{(fig:[^}]+)\}'
    matches = re.findall(pattern, content)
    return matches

def extract_figure_refs(tex_file):
    """提取所有图片引用"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \ref{fig:...}
    pattern = r'\\ref\{(fig:[^}]+)\}'
    matches = re.findall(pattern, content)
    return matches

def extract_citations(tex_file):
    """提取所有文献引用"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 \cite{...}
    pattern = r'\\cite\{([^}]+)\}'
    matches = re.findall(pattern, content)
    
    # 展开多个引用
    all_cites = []
    for match in matches:
        cites = [c.strip() for c in match.split(',')]
        all_cites.extend(cites)
    
    return all_cites

def extract_bib_entries(bib_file):
    """提取 bib 文件中的所有条目"""
    if not os.path.exists(bib_file):
        return []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 @article{key, @inproceedings{key, 等
    pattern = r'@\w+\{([^,]+),'
    matches = re.findall(pattern, content)
    return matches

def check_file_exists(filepath, base_dir='COMBINED'):
    """检查文件是否存在"""
    # 尝试多种可能的路径
    possible_paths = [
        filepath,
        os.path.join(base_dir, filepath),
        os.path.join(base_dir, 'figures', os.path.basename(filepath)),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return True, path
    
    return False, None

def main():
    print("=" * 80)
    print("论文引用完整性检查")
    print("=" * 80)
    
    # 文件路径
    english_tex = 'COMBINED/paper_english.tex'
    chinese_tex = 'COMBINED/paper_chinese.tex'
    bib_file = 'COMBINED/references.bib'
    figures_dir = 'COMBINED/figures'
    
    # ========== 检查英文版 ==========
    print("\n" + "=" * 80)
    print("📄 英文版论文 (paper_english.tex)")
    print("=" * 80)
    
    # 1. 图片引用检查
    print("\n1️⃣  图片引用检查")
    print("-" * 80)
    
    figure_files = extract_figure_references(english_tex)
    print(f"\n找到 {len(figure_files)} 个图片引用：\n")
    
    missing_figures = []
    for i, fig in enumerate(figure_files, 1):
        exists, actual_path = check_file_exists(fig)
        status = "✅" if exists else "❌"
        print(f"{status} {i:2d}. {fig}")
        if exists:
            print(f"       → 实际路径: {actual_path}")
        else:
            print(f"       → ⚠️  文件不存在！")
            missing_figures.append(fig)
    
    # 2. 图片标签和引用检查
    print("\n2️⃣  图片标签和引用匹配检查")
    print("-" * 80)
    
    fig_labels = extract_figure_labels(english_tex)
    fig_refs = extract_figure_refs(english_tex)
    
    print(f"\n定义的图片标签 ({len(fig_labels)} 个):")
    for label in sorted(set(fig_labels)):
        count = fig_labels.count(label)
        status = "⚠️  重复" if count > 1 else "✅"
        print(f"  {status} {label} (定义 {count} 次)")
    
    print(f"\n引用的图片标签 ({len(set(fig_refs))} 个):")
    for ref in sorted(set(fig_refs)):
        count = fig_refs.count(ref)
        in_labels = "✅" if ref in fig_labels else "❌ 未定义"
        print(f"  {in_labels} {ref} (引用 {count} 次)")
    
    # 检查未引用的标签
    unreferenced_figs = set(fig_labels) - set(fig_refs)
    if unreferenced_figs:
        print(f"\n⚠️  定义但未引用的图片标签:")
        for label in sorted(unreferenced_figs):
            print(f"  - {label}")
    
    # 检查未定义的引用
    undefined_fig_refs = set(fig_refs) - set(fig_labels)
    if undefined_fig_refs:
        print(f"\n❌ 引用但未定义的图片标签:")
        for ref in sorted(undefined_fig_refs):
            print(f"  - {ref}")
    
    # 3. 表格标签和引用检查
    print("\n3️⃣  表格标签和引用匹配检查")
    print("-" * 80)
    
    tab_labels = extract_table_labels(english_tex)
    tab_refs = extract_table_refs(english_tex)
    
    print(f"\n定义的表格标签 ({len(tab_labels)} 个):")
    for label in sorted(set(tab_labels)):
        count = tab_labels.count(label)
        status = "⚠️  重复" if count > 1 else "✅"
        print(f"  {status} {label} (定义 {count} 次)")
    
    print(f"\n引用的表格标签 ({len(set(tab_refs))} 个):")
    for ref in sorted(set(tab_refs)):
        count = tab_refs.count(ref)
        in_labels = "✅" if ref in tab_labels else "❌ 未定义"
        print(f"  {in_labels} {ref} (引用 {count} 次)")
    
    # 检查未引用的标签
    unreferenced_tabs = set(tab_labels) - set(tab_refs)
    if unreferenced_tabs:
        print(f"\n⚠️  定义但未引用的表格标签:")
        for label in sorted(unreferenced_tabs):
            print(f"  - {label}")
    
    # 检查未定义的引用
    undefined_tab_refs = set(tab_refs) - set(tab_labels)
    if undefined_tab_refs:
        print(f"\n❌ 引用但未定义的表格标签:")
        for ref in sorted(undefined_tab_refs):
            print(f"  - {ref}")
    
    # 4. 文献引用检查
    print("\n4️⃣  文献引用检查")
    print("-" * 80)
    
    citations = extract_citations(english_tex)
    bib_entries = extract_bib_entries(bib_file)
    
    print(f"\n论文中引用的文献 ({len(set(citations))} 个不同条目):")
    
    missing_bibs = []
    for cite in sorted(set(citations)):
        count = citations.count(cite)
        in_bib = "✅" if cite in bib_entries else "❌ 缺失"
        print(f"  {in_bib} {cite} (引用 {count} 次)")
        if cite not in bib_entries:
            missing_bibs.append(cite)
    
    # 检查未引用的 bib 条目
    unreferenced_bibs = set(bib_entries) - set(citations)
    if unreferenced_bibs:
        print(f"\n⚠️  BibTeX 中定义但未引用的文献 ({len(unreferenced_bibs)} 个):")
        for bib in sorted(unreferenced_bibs):
            print(f"  - {bib}")
    
    # ========== 检查中文版 ==========
    print("\n\n" + "=" * 80)
    print("📄 中文版论文 (paper_chinese.tex)")
    print("=" * 80)
    
    # 1. 图片引用检查
    print("\n1️⃣  图片引用检查")
    print("-" * 80)
    
    figure_files_cn = extract_figure_references(chinese_tex)
    print(f"\n找到 {len(figure_files_cn)} 个图片引用：\n")
    
    missing_figures_cn = []
    for i, fig in enumerate(figure_files_cn, 1):
        exists, actual_path = check_file_exists(fig)
        status = "✅" if exists else "❌"
        print(f"{status} {i:2d}. {fig}")
        if exists:
            print(f"       → 实际路径: {actual_path}")
        else:
            print(f"       → ⚠️  文件不存在！")
            missing_figures_cn.append(fig)
    
    # 2. 图片标签和引用检查
    print("\n2️⃣  图片标签和引用匹配检查")
    print("-" * 80)
    
    fig_labels_cn = extract_figure_labels(chinese_tex)
    fig_refs_cn = extract_figure_refs(chinese_tex)
    
    print(f"\n定义的图片标签 ({len(fig_labels_cn)} 个):")
    for label in sorted(set(fig_labels_cn)):
        count = fig_labels_cn.count(label)
        status = "⚠️  重复" if count > 1 else "✅"
        print(f"  {status} {label} (定义 {count} 次)")
    
    print(f"\n引用的图片标签 ({len(set(fig_refs_cn))} 个):")
    for ref in sorted(set(fig_refs_cn)):
        count = fig_refs_cn.count(ref)
        in_labels = "✅" if ref in fig_labels_cn else "❌ 未定义"
        print(f"  {in_labels} {ref} (引用 {count} 次)")
    
    # 3. 表格标签和引用检查
    print("\n3️⃣  表格标签和引用匹配检查")
    print("-" * 80)
    
    tab_labels_cn = extract_table_labels(chinese_tex)
    tab_refs_cn = extract_table_refs(chinese_tex)
    
    print(f"\n定义的表格标签 ({len(tab_labels_cn)} 个):")
    for label in sorted(set(tab_labels_cn)):
        count = tab_labels_cn.count(label)
        status = "⚠️  重复" if count > 1 else "✅"
        print(f"  {status} {label} (定义 {count} 次)")
    
    print(f"\n引用的表格标签 ({len(set(tab_refs_cn))} 个):")
    for ref in sorted(set(tab_refs_cn)):
        count = tab_refs_cn.count(ref)
        in_labels = "✅" if ref in tab_labels_cn else "❌ 未定义"
        print(f"  {in_labels} {ref} (引用 {count} 次)")
    
    # 4. 文献引用检查
    print("\n4️⃣  文献引用检查")
    print("-" * 80)
    
    citations_cn = extract_citations(chinese_tex)
    
    print(f"\n论文中引用的文献 ({len(set(citations_cn))} 个不同条目):")
    
    missing_bibs_cn = []
    for cite in sorted(set(citations_cn)):
        count = citations_cn.count(cite)
        in_bib = "✅" if cite in bib_entries else "❌ 缺失"
        print(f"  {in_bib} {cite} (引用 {count} 次)")
        if cite not in bib_entries:
            missing_bibs_cn.append(cite)
    
    # ========== 总结 ==========
    print("\n\n" + "=" * 80)
    print("📊 检查总结")
    print("=" * 80)
    
    print("\n🔍 英文版问题汇总:")
    print("-" * 80)
    
    total_issues_en = 0
    
    if missing_figures:
        print(f"\n❌ 缺失的图片文件 ({len(missing_figures)} 个):")
        for fig in missing_figures:
            print(f"  - {fig}")
        total_issues_en += len(missing_figures)
    else:
        print("\n✅ 所有图片文件都存在")
    
    if undefined_fig_refs:
        print(f"\n❌ 未定义的图片引用 ({len(undefined_fig_refs)} 个):")
        for ref in sorted(undefined_fig_refs):
            print(f"  - {ref}")
        total_issues_en += len(undefined_fig_refs)
    else:
        print("✅ 所有图片引用都有定义")
    
    if undefined_tab_refs:
        print(f"\n❌ 未定义的表格引用 ({len(undefined_tab_refs)} 个):")
        for ref in sorted(undefined_tab_refs):
            print(f"  - {ref}")
        total_issues_en += len(undefined_tab_refs)
    else:
        print("✅ 所有表格引用都有定义")
    
    if missing_bibs:
        print(f"\n❌ 缺失的文献条目 ({len(missing_bibs)} 个):")
        for bib in sorted(missing_bibs):
            print(f"  - {bib}")
        total_issues_en += len(missing_bibs)
    else:
        print("✅ 所有文献引用都在 BibTeX 中")
    
    print(f"\n英文版总计问题: {total_issues_en} 个")
    
    print("\n🔍 中文版问题汇总:")
    print("-" * 80)
    
    total_issues_cn = 0
    
    if missing_figures_cn:
        print(f"\n❌ 缺失的图片文件 ({len(missing_figures_cn)} 个):")
        for fig in missing_figures_cn:
            print(f"  - {fig}")
        total_issues_cn += len(missing_figures_cn)
    else:
        print("\n✅ 所有图片文件都存在")
    
    undefined_fig_refs_cn = set(fig_refs_cn) - set(fig_labels_cn)
    if undefined_fig_refs_cn:
        print(f"\n❌ 未定义的图片引用 ({len(undefined_fig_refs_cn)} 个):")
        for ref in sorted(undefined_fig_refs_cn):
            print(f"  - {ref}")
        total_issues_cn += len(undefined_fig_refs_cn)
    else:
        print("✅ 所有图片引用都有定义")
    
    undefined_tab_refs_cn = set(tab_refs_cn) - set(tab_labels_cn)
    if undefined_tab_refs_cn:
        print(f"\n❌ 未定义的表格引用 ({len(undefined_tab_refs_cn)} 个):")
        for ref in sorted(undefined_tab_refs_cn):
            print(f"  - {ref}")
        total_issues_cn += len(undefined_tab_refs_cn)
    else:
        print("✅ 所有表格引用都有定义")
    
    if missing_bibs_cn:
        print(f"\n❌ 缺失的文献条目 ({len(missing_bibs_cn)} 个):")
        for bib in sorted(missing_bibs_cn):
            print(f"  - {bib}")
        total_issues_cn += len(missing_bibs_cn)
    else:
        print("✅ 所有文献引用都在 BibTeX 中")
    
    print(f"\n中文版总计问题: {total_issues_cn} 个")
    
    print("\n" + "=" * 80)
    if total_issues_en == 0 and total_issues_cn == 0:
        print("🎉 恭喜！所有引用都完整无误！")
    else:
        print(f"⚠️  发现 {total_issues_en + total_issues_cn} 个问题需要修复")
    print("=" * 80)

if __name__ == '__main__':
    main()

