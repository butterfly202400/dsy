import requests
import base64
import re
from datetime import datetime

# 1. 订阅源
urls = ["https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"]

# 2. 定义识别字典（已加入芬兰、荷兰，并按你之前的偏好排序）
REGION_MAP = [
    ('新加坡', ['SG', 'SINGAPORE', '新', '獅城']),
    ('法国', ['FR', 'FRANCE', '法']),
    ('芬兰', ['FI', 'FINLAND', '芬兰', '芬']),
    ('荷兰', ['NL', 'NETHERLANDS', '荷兰', '荷']), # 新增荷兰
    ('加拿大', ['CA', 'CANADA', '加拿大', '加']),
    ('美国', ['US', 'USA', 'UNITED STATES', '美国', '美', 'AMERICA']),
    ('日本', ['JP', 'JAPAN', '日本', '日', '东京', '大阪']),
    ('英国', ['UK', 'GB', 'UNITED KINGDOM', '英国', '英']),
    ('澳大利亚', ['AU', 'AUSTRALIA', '澳大利亚', '澳']),
    ('台湾', ['TW', 'TAIWAN', '台湾', '台']),
    ('香港', ['HK', 'HONG KONG', '香港', '港']),
    ('韩国', ['KR', 'KOREA', '韩国', '韩', '首尔']),
    ('德国', ['DE', 'GERMANY', '德国', '德'])
]

def safe_decode(data):
    try:
        data = data.strip()
        if not data: return ""
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except: return ""

def find_country(remark):
    """在备注全文中智能搜索国家关键词"""
    remark_upper = remark.upper()
    for name, keywords in REGION_MAP:
        for kw in keywords:
            # 匹配关键词，增加简单的边界判断
            if kw.upper() in remark_upper:
                return name
    return None

def main():
    country_groups = {name: set() for name, _ in REGION_MAP}
    country_groups['其他'] = set()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 启动全量识别抓取（含芬兰、荷兰）...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                raw_data = resp.text
                # 兼容 Base64 订阅源和明文订阅源
                content = safe_decode(raw_data) if "://" not in raw_data[:50] else raw_data
                
                for line in content.splitlines():
                    line = line.strip()
                    if "://" in line:
                        parts = line.split("#")
                        protocol = parts[0]
                        # 获取原始备注，如果没有备注则设为 Node
                        raw_remark = parts[1] if len(parts) > 1 else "Node"
                        
                        # 扫描备注匹配国家
                        country_name = find_country(raw_remark)
                        
                        if country_name:
                            country_groups[country_name].add(protocol)
                        else:
                            # 没识别出来的保留原备注的前10位
                            country_groups['其他'].add(f"{protocol}#未知_{raw_remark[:10]}")
        except Exception as e:
            print(f"抓取失败: {e}")

    final_nodes = []
    # 按照 REGION_MAP 的顺序排列
    for country_name, _ in REGION_MAP:
        nodes = sorted(list(country_groups[country_name]))
        for i, protocol in enumerate(nodes, 1):
            final_nodes.append(f"{protocol}#{country_name} {i:02d}")
    
    # 最后加上无法识别的节点
    others = sorted(list(country_groups['其他']))
    for i, node in enumerate(others, 1):
        final_nodes.append(f"{node} {i:02d}")

    # 保存明文预览
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_nodes))
    
    # 保存加密订阅
    final_content = "\n".join(final_nodes)
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(final_content.encode('utf-8')).decode('utf-8'))
    
    print(f"同步完成！总计捕获 {len(final_nodes)} 个节点。")

if __name__ == "__main__":
    main()
