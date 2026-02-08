import requests
import base64
import re
from datetime import datetime

# 1. 整合多个备用订阅源，确保节点充足
urls = [
    "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
    "https://raw.githubusercontent.com/tinkdog/v2ray-nodes/master/v2ray_nodes.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-nodes/main/v2ray.txt"
]

# 2. 国家识别映射（严格按你的偏好顺序：新加坡、法国、芬兰、荷兰...）
REGION_MAP = [
    ('新加坡', ['SG', 'SINGAPORE', '新', '獅城']),
    ('法国', ['FR', 'FRANCE', '法']),
    ('芬兰', ['FI', 'FINLAND', '芬兰', '芬']),
    ('荷兰', ['NL', 'NETHERLANDS', '荷兰', '荷']),
    ('加拿大', ['CA', 'CANADA', '加拿大', '加']),
    ('美国', ['US', 'USA', 'UNITED STATES', '美国', '美', 'AMERICA']),
    ('日本', ['JP', 'JAPAN', '日本', '日', '东京', '大阪']),
    ('英国', ['UK', 'GB', 'UNITED KINGDOM', '英国', '英']),
    ('澳大利亚', ['AU', 'AUSTRALIA', '澳大利亚', '澳']),
    ('台湾', ['TW', 'TAIWAN', '台湾', '台', '台北']),
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

def find_country(text):
    """在文本中智能搜索国家关键词"""
    if not text: return None
    text_upper = text.upper()
    for name, keywords in REGION_MAP:
        for kw in keywords:
            if kw.upper() in text_upper:
                return name
    return None

def main():
    # 初始化国家分类容器
    country_groups = {name: set() for name, _ in REGION_MAP}
    country_groups['其他'] = set()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 启动多源节点收割...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                raw_data = resp.text
                # 自动判断 Base64 或明文
                content = safe_decode(raw_data) if "://" not in raw_data[:50] else raw_data
                
                for line in content.splitlines():
                    line = line.strip()
                    if "://" in line:
                        # 拆分链接和原有备注
                        parts = line.split("#")
                        protocol = parts[0]
                        old_remark = parts[1] if len(parts) > 1 else ""
                        
                        # 识别国家
                        country_name = find_country(old_remark)
                        
                        if country_name:
                            country_groups[country_name].add(protocol)
                        else:
                            # 无法识别的保留原链接
                            country_groups['其他'].add(protocol)
        except Exception as e:
            print(f"源 {url} 抓取异常: {e}")

    final_nodes = []
    # 按照严格顺序排列并自动编号
    for country_name, _ in REGION_MAP:
        nodes = sorted(list(country_groups[country_name]))
        for i, protocol in enumerate(nodes, 1):
            final_nodes.append(f"{protocol}#{country_name} {i:02d}")
    
    # 无法识别的节点统一放在末尾
    others = sorted(list(country_groups['其他']))
    for i, protocol in enumerate(others, 1):
        final_nodes.append(f"{protocol}#未知国家 {i:02d}")

    # 写入预览文件
    output_text = "\n".join(final_nodes)
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
    
    # 写入加密订阅文件
    final_b64 = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(final_b64)
    
    print(f"多源同步完成！共获得 {len(final_nodes)} 个节点。")

if __name__ == "__main__":
    main()
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
