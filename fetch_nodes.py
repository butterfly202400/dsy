import requests
import base64
import re
from datetime import datetime

# 1. 订阅源（已补充你提供的 4 个新地址）
urls = [
    "https://raw.githubusercontent.com/ssrsub/ssr/master/v2ray",
    "https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
    "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202602072",
    "https://ghfast.top/https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub1.txt",
    "https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/all_configs.txt",
    "https://raw.githubusercontent.com/NiREvil/vless/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-worker-dotnet/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2"
]

# 2. 允许的地区及关键词（包含芬兰及其他 9 个地区）
ALLOWED_REGIONS = {
    '美国': ['US', 'USA', 'United States', '美国', '美'],
    '香港': ['HK', 'Hong Kong', '香港', '港'],
    '日本': ['JP', 'Japan', '日本', '日'],
    '新加坡': ['SG', 'Singapore', '新加坡', '新'],
    '台湾': ['TW', 'Taiwan', '台湾', '台'],
    '德国': ['DE', 'Germany', '德国', '德'],
    '法国': ['FR', 'France', '法国', '法'],
    '荷兰': ['NL', 'Netherlands', '荷兰', '荷'],
    '加拿大': ['CA', 'Canada', '加拿大', '加'],
    '芬兰': ['FI', 'Finland', '芬兰', '芬']
}

# 3. 广告关键词
AD_KEYWORDS = ["加入频道", "订阅说明", "广告", "收费", "频道", "t.me", "Fixed by", "Owner", "免费"]

def safe_decode(data):
    try:
        data = data.strip()
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except: return data

def get_region(node_str):
    """识别节点所属地区"""
    upper_node = node_str.upper()
    if "#" in upper_node:
        remark = upper_node.split("#")[-1]
        for region, keywords in ALLOWED_REGIONS.items():
            for kw in keywords:
                if kw.upper() in remark:
                    return region
    return None

def main():
    # 使用字典归类节点： { '美国': {协议1, 协议2}, '香港': {协议1} }
    region_groups = {r: set() for r in ALLOWED_REGIONS.keys()}
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在抓取并按地区排序...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                content = safe_decode(resp.text)
                for line in content.splitlines():
                    line = line.strip()
                    if any(line.startswith(p) for p in ['vmess://', 'vless://', 'ss://', 'ssr://', 'trojan://']):
                        reg = get_region(line)
                        if reg:
                            # 提取协议部分，清洗旧备注
                            protocol_part = line.split("#")[0]
                            region_groups[reg].add(protocol_part)
        except: continue

    final_nodes = []
    # 按照地区名称排序并重新生成带编号的备注
    for region in sorted(region_groups.keys()):
        nodes = sorted(list(region_groups[region]))
        for i, protocol in enumerate(nodes, 1):
            # 格式： 地区 01
            new_node = f"{protocol}#{region} {i:02d}"
            final_nodes.append(new_node)

    # 保存明文
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_nodes))
    
    # 保存加密订阅
    final_b64 = base64.b64encode("\n".join(final_nodes).encode('utf-8')).decode('utf-8')
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(final_b64)
    
    print(f"任务完成！共捕获目标地区节点: {len(final_nodes)} 个")

if __name__ == "__main__":
    main()
