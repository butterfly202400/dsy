import requests
import base64
import re
from datetime import datetime

# 1. 锁定唯一订阅源
urls = [
    "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"
]

# 2. 增强版：严格按顺序排列的国家/地区关键词映射
# 增加了城市名和更多缩写，提高识别率
ORDERED_REGIONS = [
    ('新加坡', ['SG', 'Singapore', '新加坡', '新', '獅城']),
    ('法国', ['FR', 'France', '法国', '法', 'French']),
    ('芬兰', ['FI', 'Finland', '芬兰', '芬']),
    ('加拿大', ['CA', 'Canada', '加拿大', '加']),
    ('美国', ['US', 'USA', 'United States', '美国', '美', 'America']),
    ('日本', ['JP', 'Japan', '日本', '日', '东京', '大阪', 'Tokyo', 'Osaka']),
    ('英国', ['UK', 'United Kingdom', '英国', '英', 'GB', 'London', '伦敦']),
    ('澳大利亚', ['AU', 'Australia', '澳大利亚', '澳', 'Sydney', 'Melbourne', 'AUS', '悉尼', '墨尔本']),
    ('台湾', ['TW', 'Taiwan', '台湾', '台', '台北', '新北', 'Taipei'])
]

# 3. 广告关键词过滤
AD_KEYWORDS = ["加入频道", "订阅说明", "广告", "收费", "频道", "t.me", "Fixed by", "Owner"]

def safe_decode(data):
    try:
        data = data.strip()
        if not data: return ""
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except: return data

def get_region_index(node_str):
    """
    更智能的地区识别：
    先预处理节点名，移除干扰符号，再匹配关键词。
    """
    # 提取备注部分
    if "#" not in node_str: return None, None
    remark = node_str.split("#")[-1].upper()
    
    # 预处理：将常见分隔符替换为空格，防止 "FR-Node" 无法识别
    clean_remark = re.sub(r'[-_./]', ' ', remark)

    for index, (name, keywords) in enumerate(ORDERED_REGIONS):
        for kw in keywords:
            # 使用正则 \b 匹配独立单词，防止 'FREE' 误判为法国 'FR'
            pattern = rf'(?:\b|[\u4e00-\u9fa5]){re.escape(kw.upper())}(?:\b|[\u4e00-\u9fa5])'
            if re.search(pattern, clean_remark) or kw.upper() in clean_remark:
                return index, name
    return None, None

def main():
    # 使用列表存储各地区的集合（去重）
    region_bins = [set() for _ in ORDERED_REGIONS]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 启动增强版排序抓取...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                content = safe_decode(resp.text)
                for line in content.splitlines():
                    line = line.strip()
                    # 识别主流协议
                    if any(line.startswith(p) for p in ['vmess://', 'vless://', 'ss://', 'ssr://', 'trojan://']):
                        idx, region_name = get_region_index(line)
                        if idx is not None:
                            # 提取协议本体，丢弃原有杂乱备注
                            protocol_part = line.split("#")[0]
                            region_bins[idx].add(protocol_part)
        except Exception as e:
            print(f"请求失败: {e}")

    final_nodes = []
    summary_report = []

    # 4. 按照预设顺序提取并生成新备注
    for idx, (region_name, _) in enumerate(ORDERED_REGIONS):
        nodes = sorted(list(region_bins[idx]))
        if nodes:
            summary_report.append(f"{region_name}: {len(nodes)}个")
            for i, protocol in enumerate(nodes, 1):
                # 统一格式： 国家 编号 (例如: 新加坡 01)
                new_node = f"{protocol}#{region_name} {i:02d}"
                final_nodes.append(new_node)

    # 5. 保存结果文件
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_nodes))
    
    final_content = "\n".join(final_nodes)
    final_b64 = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(final_b64)
    
    # 打印最终报告
    print("-" * 30)
    print(f"同步完成！总计节点: {len(final_nodes)} 个")
    print("地区统计: " + " | ".join(summary_report))
    print("-" * 30)

if __name__ == "__main__":
    main()
