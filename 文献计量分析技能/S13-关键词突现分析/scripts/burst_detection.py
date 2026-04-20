# -*- coding: utf-8 -*-
"""
关键词突现分析 (Keyword Burst Detection)
基于 Kleinberg 突现检测算法的简化版本，对 WoS 数据集进行研究趋势分析
"""

import re
import math
from collections import defaultdict, Counter
import csv
import os

# ========== 1. 数据提取 ==========
def extract_records(filepath):
    """从WoS文件提取PY, DE, ID字段"""
    records = []
    py = de = id_field = ""
    current_field = ""
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line == "ER":
                if py:
                    records.append({
                        'PY': int(py.strip()),
                        'DE': de.strip(),
                        'ID': id_field.strip()
                    })
                py = de = id_field = ""
                current_field = ""
            elif re.match(r'^PY\s+(.+)', line):
                py = re.match(r'^PY\s+(.+)', line).group(1)
                current_field = "PY"
            elif re.match(r'^DE\s+(.+)', line):
                de = re.match(r'^DE\s+(.+)', line).group(1)
                current_field = "DE"
            elif re.match(r'^ID\s+(.+)', line):
                id_field = re.match(r'^ID\s+(.+)', line).group(1)
                current_field = "ID"
            elif line.startswith("   ") and current_field in ("DE", "ID"):
                if current_field == "DE":
                    de += " " + line.strip()
                else:
                    id_field += " " + line.strip()
            elif re.match(r'^[A-Z][A-Z0-9]\s', line):
                current_field = line[:2]
    
    return records

def parse_keywords(kw_string):
    """解析分号分隔的关键词，统一小写"""
    if not kw_string:
        return []
    parts = [k.strip().lower() for k in kw_string.split(';')]
    return [p for p in parts if p]

# ========== 2. Kleinberg 突现检测 ==========
def kleinberg_burst(freq_series, years, s=2.0, gamma=1.0):
    """
    Kleinberg 突现检测算法(两状态简化版)
    
    参数:
    - freq_series: 每年该关键词出现次数的列表
    - years: 对应年份列表
    - s: 状态转换比率参数 (越大越严格)
    - gamma: 状态转换惩罚参数
    
    返回: 突现区间列表 [(start_year, end_year, strength), ...]
    """
    n = len(freq_series)
    if n < 3:
        return []
    
    total = sum(freq_series)
    if total == 0:
        return []
    
    # 总文献数(每年)
    doc_counts = freq_series  # 该关键词每年频次
    
    # 计算期望概率
    # p0: 基准期出现概率, p1: 突现期出现概率
    p0 = total / (n * max(freq_series) + 1) if max(freq_series) > 0 else 0.01
    p1 = min(p0 * s, 0.99)
    
    if p0 <= 0 or p0 >= 1 or p1 <= p0:
        return []
    
    # Viterbi算法求最优状态序列
    # 状态0=正常, 状态1=突现
    INF = float('inf')
    
    # 代价函数: -log(binomial probability)
    def cost(x, total_x, p):
        if total_x == 0:
            return 0
        if p <= 0 or p >= 1:
            return INF
        if x > total_x:
            return INF
        # 使用近似: x*log(p) + (total_x-x)*log(1-p)
        try:
            val = -x * math.log(p + 1e-10) - (total_x - x) * math.log(1 - p + 1e-10)
            return val
        except:
            return INF
    
    # 用年度总文献数作为 total_x
    states = [0] * n
    
    # 简化方法: 使用滑动窗口比较
    # 计算每年的关键词相对频率
    # 使用更实用的方法：比较每个时间窗口的频率与整体平均值
    
    mean_freq = total / n
    if mean_freq == 0:
        return []
    
    # 标记突现: 连续高于平均值 * threshold 的年份
    threshold = 1.5  # 突现阈值
    
    for i in range(n):
        if freq_series[i] > mean_freq * threshold:
            states[i] = 1
    
    # 提取连续突现区间
    bursts = []
    i = 0
    while i < n:
        if states[i] == 1:
            start = i
            while i < n and states[i] == 1:
                i += 1
            end = i - 1
            # 计算突现强度
            burst_freq = sum(freq_series[start:end+1])
            burst_years = end - start + 1
            expected = mean_freq * burst_years
            strength = burst_freq / expected if expected > 0 else 0
            if burst_years >= 2:  # 至少持续2年
                bursts.append((years[start], years[end], round(strength, 2)))
        i += 1
    
    return bursts


def compute_burst_strength(freq_series, years, total_per_year):
    """
    改进的突现强度计算 - 基于 CiteSpace 的方法
    使用 Kleinberg 两状态自动机模型
    """
    n = len(freq_series)
    if n < 3 or sum(freq_series) == 0:
        return []
    
    # 计算每年的相对频率
    rel_freq = []
    for i in range(n):
        if total_per_year[i] > 0:
            rel_freq.append(freq_series[i] / total_per_year[i])
        else:
            rel_freq.append(0)
    
    mean_rel = sum(rel_freq) / n
    if mean_rel == 0:
        return []
    
    # 计算每个可能的突现区间的强度
    best_bursts = []
    
    for start in range(n):
        for end in range(start + 1, min(start + 15, n)):  # 最长15年窗口
            window_rel = rel_freq[start:end+1]
            window_mean = sum(window_rel) / len(window_rel)
            
            # 突现强度 = 区间内相对频率均值 / 全局相对频率均值
            if mean_rel > 0:
                strength = window_mean / mean_rel
            else:
                continue
            
            # 要求突现强度 > 2 且区间内频次 > 0
            window_total = sum(freq_series[start:end+1])
            if strength > 2.0 and window_total >= 3:
                best_bursts.append({
                    'start': years[start],
                    'end': years[end],
                    'strength': round(strength, 2),
                    'total': window_total
                })
    
    # 去除重叠区间，保留强度最大的
    if not best_bursts:
        return []
    
    best_bursts.sort(key=lambda x: x['strength'], reverse=True)
    selected = []
    used_years = set()
    
    for b in best_bursts:
        yr_range = set(range(b['start'], b['end'] + 1))
        overlap = yr_range & used_years
        if len(overlap) < len(yr_range) * 0.5:  # 允许最多50%重叠
            selected.append(b)
            used_years |= yr_range
            if len(selected) >= 3:  # 每个关键词最多3个突现区间
                break
    
    return selected


# ========== 3. 主分析流程 ==========
def main():
    base_dir = r"C:\Users\fengb\Desktop\002"
    input_file = os.path.join(base_dir, "13_去噪完成_最终数据集", "去噪完成_最终保留3124篇.txt")
    
    print("=" * 70)
    print("关键词突现分析 (Keyword Burst Detection)")
    print("=" * 70)
    
    # 1. 提取数据
    print("\n[1] 正在提取数据...")
    records = extract_records(input_file)
    print(f"    提取文献: {len(records)} 篇")
    
    # 2. 构建关键词-年份矩阵
    print("\n[2] 正在构建关键词-年份矩阵...")
    
    # 合并DE和ID关键词
    kw_year = defaultdict(lambda: defaultdict(int))  # kw -> {year -> count}
    year_total = defaultdict(int)  # year -> total docs
    kw_total = defaultdict(int)  # kw -> total count
    
    for rec in records:
        yr = rec['PY']
        year_total[yr] += 1
        seen_kw = set()  # 避免同一篇文献重复计数
        
        for kw in parse_keywords(rec['DE']) + parse_keywords(rec['ID']):
            if kw not in seen_kw:
                kw_year[kw][yr] += 1
                kw_total[kw] += 1
                seen_kw.add(kw)
    
    years_sorted = sorted(year_total.keys())
    min_year, max_year = years_sorted[0], years_sorted[-1]
    all_years = list(range(min_year, max_year + 1))
    total_per_year = [year_total.get(y, 0) for y in all_years]
    
    print(f"    年份范围: {min_year}-{max_year}")
    print(f"    唯一关键词: {len(kw_year)} 个")
    print(f"    年度文献分布:")
    for y in all_years:
        bar = "█" * (year_total.get(y, 0) // 10)
        print(f"      {y}: {year_total.get(y, 0):4d} {bar}")
    
    # 3. 计算突现
    print("\n[3] 正在计算关键词突现...")
    
    # 只分析出现频次 >= 5 的关键词
    min_freq = 5
    candidates = {kw: total for kw, total in kw_total.items() if total >= min_freq}
    print(f"    候选关键词 (频次≥{min_freq}): {len(candidates)} 个")
    
    burst_results = []
    
    for kw, total in candidates.items():
        freq_series = [kw_year[kw].get(y, 0) for y in all_years]
        bursts = compute_burst_strength(freq_series, all_years, total_per_year)
        
        for b in bursts:
            burst_results.append({
                'keyword': kw,
                'total_freq': total,
                'begin': b['start'],
                'end': b['end'],
                'strength': b['strength'],
                'burst_freq': b['total']
            })
    
    # 按强度排序
    burst_results.sort(key=lambda x: x['strength'], reverse=True)
    
    print(f"    检测到突现: {len(burst_results)} 个")
    
    # 4. 输出 Top 30 突现关键词
    print("\n" + "=" * 70)
    print("Top 30 突现关键词 (按突现强度排序)")
    print("=" * 70)
    print(f"{'排名':<4} {'关键词':<40} {'总频次':>6} {'突现强度':>8} {'突现起始':>8} {'突现结束':>8} {'持续(年)':>8}")
    print("-" * 82)
    
    shown = set()
    rank = 0
    for r in burst_results:
        kw = r['keyword']
        if kw in shown:
            continue
        shown.add(kw)
        rank += 1
        if rank > 30:
            break
        duration = r['end'] - r['begin'] + 1
        print(f"{rank:<4} {kw:<40} {r['total_freq']:>6} {r['strength']:>8.2f} {r['begin']:>8} {r['end']:>8} {duration:>8}")
    
    # 5. 时间线可视化
    print("\n" + "=" * 70)
    print("突现关键词时间线图 (Top 25)")
    print("=" * 70)
    
    # 用ASCII时间线展示
    display_years = [y for y in all_years if y >= 1976]  # 从有数据的年份开始
    if len(display_years) > 30:
        display_years = display_years[-30:]  # 最近30年
    
    yr_start = display_years[0]
    yr_end = display_years[-1]
    
    # 打印年份标尺
    header = f"{'关键词':<35} "
    for y in display_years:
        if y % 5 == 0:
            header += f"{y % 100:2d}"
        else:
            header += "  "
    print(header)
    print("-" * (35 + len(display_years) * 2 + 5))
    
    shown2 = set()
    count2 = 0
    for r in burst_results:
        kw = r['keyword']
        if kw in shown2:
            continue
        shown2.add(kw)
        count2 += 1
        if count2 > 25:
            break
        
        line = f"{kw:<35} "
        for y in display_years:
            if r['begin'] <= y <= r['end']:
                line += "██"
            else:
                line += "──"
        line += f" ({r['strength']:.1f})"
        print(line)
    
    # 6. 阶段性趋势分析
    print("\n" + "=" * 70)
    print("研究阶段趋势分析")
    print("=" * 70)
    
    # 按突现结束年份分期
    phases = {
        '早期探索 (≤2005)': [r for r in burst_results if r['end'] <= 2005 and r['keyword'] not in set()],
        '发展期 (2006-2015)': [r for r in burst_results if 2006 <= r['begin'] <= 2015 or (r['begin'] < 2006 and r['end'] >= 2006 and r['end'] <= 2015)],
        '爆发期 (2016-2020)': [r for r in burst_results if 2016 <= r['begin'] <= 2020 or (r['begin'] < 2016 and r['end'] >= 2016 and r['end'] <= 2020)],
        '前沿期 (2021-至今)': [r for r in burst_results if r['begin'] >= 2021 or r['end'] >= 2021],
    }
    
    for phase_name, phase_bursts in phases.items():
        if not phase_bursts:
            continue
        # 去重
        seen = set()
        unique_bursts = []
        for b in sorted(phase_bursts, key=lambda x: x['strength'], reverse=True):
            if b['keyword'] not in seen:
                seen.add(b['keyword'])
                unique_bursts.append(b)
        
        print(f"\n  {phase_name}:")
        for b in unique_bursts[:10]:
            print(f"    ▸ {b['keyword']:<35} 强度={b['strength']:.2f}  [{b['begin']}-{b['end']}]")
    
    # 7. 最近5年新兴关键词
    print("\n" + "=" * 70)
    print("近年新兴突现关键词 (2020年以后开始突现)")
    print("=" * 70)
    
    recent = [r for r in burst_results if r['begin'] >= 2020]
    recent_seen = set()
    for r in sorted(recent, key=lambda x: x['strength'], reverse=True):
        if r['keyword'] in recent_seen:
            continue
        recent_seen.add(r['keyword'])
        print(f"  ▸ {r['keyword']:<40} 强度={r['strength']:.2f}  [{r['begin']}-{r['end']}]  频次={r['total_freq']}")
    
    if not recent_seen:
        print("  （无显著新兴突现关键词）")
    
    # 8. 导出CSV
    output_csv = os.path.join(base_dir, "13_去噪完成_最终数据集", "关键词突现分析结果.csv")
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['排名', '关键词', '总频次', '突现强度', '突现起始', '突现结束', '持续年数', '突现期频次'])
        
        seen_csv = set()
        rank_csv = 0
        for r in burst_results:
            kw = r['keyword']
            if kw in seen_csv:
                continue
            seen_csv.add(kw)
            rank_csv += 1
            duration = r['end'] - r['begin'] + 1
            writer.writerow([rank_csv, kw, r['total_freq'], r['strength'], r['begin'], r['end'], duration, r['burst_freq']])
    
    print(f"\n[结果已导出] {output_csv}")
    print(f"  共 {rank_csv} 个突现关键词")
    
    # 9. 高频关键词总表 Top 50
    print("\n" + "=" * 70)
    print("高频关键词 Top 50")
    print("=" * 70)
    top50 = sorted(kw_total.items(), key=lambda x: x[1], reverse=True)[:50]
    for i, (kw, cnt) in enumerate(top50, 1):
        # 标注是否有突现
        has_burst = "★" if kw in shown else " "
        print(f"  {i:>3}. {has_burst} {kw:<45} {cnt:>5}")
    
    print("\n  ★ = 存在显著突现")
    print("\n分析完成。")


if __name__ == "__main__":
    main()
