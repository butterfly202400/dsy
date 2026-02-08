import requests
import base64
from datetime import datetime

# 1. 锁定唯一订阅源
urls = [
    "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"
]

# 2. 简化的地区映射：严格按你指定的顺序排列
ORDERED_REGIONS = [
    ('新加坡', ['SG', 'Singapore', '新加坡', '新']),
    ('法国', ['FR', 'France', '法国', '法']),
    ('芬兰', ['FI', 'Finland', '芬兰', '芬']),
    ('加拿大', ['CA', 'Canada', '加拿大', '加']),
    ('美国', ['US', 'USA', 'United States', '美国', '美']),
    ('日本', ['JP', 'Japan', '日本', '日', '东京', '大阪']),
    ('英国', ['UK', 'United Kingdom', '英国', '英', 'GB']),
    ('澳大利亚', ['AU', 'Australia', '澳大利亚', '澳', 'SYD']),
    ('台湾', ['TW', 'Taiwan', '台湾', '台'])
]

def safe_decode(data):
    try:
        data = data.strip()
        if not data: return ""
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except: return data

def get_region_index(node_str):
    """弱化匹配：备注中只要包含关键词就抓取"""
    if "#" not in node_str: return None, None
    remark = node_str.split("#")[-1].upper()
    
    for index, (name, keywords) in enumerate(ORDERED_REGIONS):
        for kw in keywords:
            if kw.upper() in remark:
                return index, name
    return None, None

def main():
    # 使用列表存储各地区的集合（自动去重）
    region_bins = [set() for _ in ORDERED_REGIONS]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 启动简化版抓取...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                content = safe_decode(resp.text)
                for line in content.splitlines():
                    line = line.strip()
                    if any(line.startswith(p) for p in ['vmess://', 'vless://', 'ss://', 'ssr://', 'trojan://']):
                        idx, region_name = get_region_index(line)
                        if idx is not None:
                            # 提取协议本体，丢弃旧备注
                            protocol_part = line.split("#")[0]
                            region_bins[idx].add(protocol_part)
        except Exception as e:
            print(f"请求失败: {e}")

    final_nodes = []
    # 按照国家顺序提取并重新生成带编号的备注
    for idx, (region_name, _) in enumerate(ORDERED_REGIONS):
        nodes = sorted(list(region_bins[idx]))
        for i, protocol in enumerate(nodes, 1):
            # 格式：国家名称 01
            new_node = f"{protocol}#{region_name} {i:02d}"
            final_nodes.append(new_node)

    # 保存明文预览文件
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_nodes))
    
    # 保存加密订阅文件
    final_content = "\n".join(final_nodes)
    final_b64 = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(final_b64)
    
    print(f"抓取完成！共捕获目标地区节点: {len(final_nodes)} 个")

if __name__ == "__main__":
    main()

