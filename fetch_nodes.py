import requests
import base64
import re
from datetime import datetime

# 1. 锁定订阅源
urls = ["https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt"]

def safe_decode(data):
    try:
        data = data.strip()
        if not data: return ""
        # 补齐 Base64 填充
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except: return ""

def extract_country_prefix(remark):
    """
    尝试从备注中提取国家前缀（如 HK, US, SG）
    如果无法识别，则归类为 'OTHER'
    """
    # 匹配开头的前两个字母，通常是国家代码
    match = re.search(r'^([A-Z]{2})', remark.upper())
    if match:
        return match.group(1)
    # 如果包含中文，尝试提取前两个中文字符
    chinese_match = re.search(r'^([\u4e00-\u9fa5]{1,2})', remark)
    if chinese_match:
        return chinese_match.group(1)
    return "UNKNOWN"

def main():
    # 使用字典存储：{ 'HK': {set of nodes}, 'US': {set of nodes} }
    country_groups = {}
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始全量抓取所有国家...")

    for url in urls:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                raw_data = resp.text
                # 判断是否需要 Base64 解码
                content = safe_decode(raw_data) if "://" not in raw_data[:50] else raw_data
                
                for line in content.splitlines():
                    line = line.strip()
                    if "://" in line:
                        # 提取节点信息
                        parts = line.split("#")
                        protocol = parts[0]
                        remark = parts[1] if len(parts) > 1 else "NoName"
                        
                        # 识别国家
                        country = extract_country_prefix(remark)
                        
                        if country not in country_groups:
                            country_groups[country] = set()
                        country_groups[country].add(protocol)
        except Exception as e:
            print(f"抓取失败: {e}")

    final_nodes = []
    # 按国家代码字母顺序排列
    for country in sorted(country_groups.keys()):
        nodes = sorted(list(country_groups[country]))
        for i, protocol in enumerate(nodes, 1):
            # 格式：国家代码 01
            final_nodes.append(f"{protocol}#{country} {i:02d}")

    # 写入预览文件
    with open("nodes_plain.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_nodes))
    
    # 写入加密订阅文件
    final_content = "\n".join(final_nodes)
    with open("sub_link.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(final_content.encode('utf-8')).decode('utf-8'))
    
    print(f"全量抓取完成！共捕获来自 {len(country_groups)} 个地区的 {len(final_nodes)} 个节点。")

if __name__ == "__main__":
    main()

