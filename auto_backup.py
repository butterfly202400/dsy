#!/usr/bin/env python3
"""
自动备份 .txt / .m3u 文件，保留最近15份，每15天备份一次。
支持通过环境变量 FORCE_BACKUP=true 强制立即备份（用于手动触发）。
"""
import os
import shutil
import datetime
import json
import sys

# ===== 配置 =====
BACKUP_DIR = "backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")
STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.json")
KEEP_LATEST = 15                 # 保留的最新备份份数
INTERVAL_HOURS = 360             # 备份间隔（小时），15天 = 360小时

os.makedirs(BACKUP_DIR, exist_ok=True)

# 获取当前北京时间（带时区）
beijing_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
print(f"当前北京时间: {beijing_time.isoformat()}")

# ===== 检查是否强制备份（通过环境变量）=====
force_backup = os.environ.get("FORCE_BACKUP", "").lower() == "true"
if force_backup:
    print("🚀 检测到 FORCE_BACKUP=true，将忽略间隔限制，强制备份！")

# ===== 检查 .gitignore 是否忽略 backup 目录 =====
gitignore_path = ".gitignore"
if os.path.exists(gitignore_path):
    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if line == BACKUP_DIR or line == BACKUP_DIR + "/":
                    print(f"⚠️ 警告：.gitignore 中包含了 '{line}'，这将导致备份文件不会被 Git 提交！")

# ===== 读取上次备份时间 =====
last_backup_time = None
diff_hours = 999.0   # 默认大间隔，确保首次运行或强制备份

if os.path.exists(STATE_FILE) and not force_backup:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_backup_time = datetime.datetime.fromisoformat(data["last_backup"])
            print(f"上次备份时间: {last_backup_time.isoformat()}")
            diff_hours = (beijing_time - last_backup_time).total_seconds() / 3600
            print(f"距离上次备份: {diff_hours:.2f} 小时")
    except Exception as e:
        print(f"状态文件读取失败，将执行备份。错误: {e}")

# ===== 判断是否需要备份 =====
if not force_backup and last_backup_time and diff_hours < INTERVAL_HOURS:
    print(f"当前间隔 {diff_hours:.1f} 小时 < {INTERVAL_HOURS} 小时，跳过本次备份。")
    sys.exit(0)

print(f"开始备份：距离上次已过 {diff_hours:.1f} 小时 (或强制备份/首次备份)...")

# ===== 执行备份 =====
timestamp = beijing_time.strftime("%Y-%m-%d_%H-%M-%S")
current_backup_path = os.path.join(BACKUP_DIR, timestamp)
os.makedirs(current_backup_path, exist_ok=True)

backup_count = 0
for file in os.listdir("."):
    if (file.endswith(".txt") or file.endswith(".m3u")) and os.path.isfile(file):
        if file == "backup_log.txt":   # 避免备份日志本身
            continue
        shutil.copy2(file, current_backup_path)
        backup_count += 1

print(f"本次备份了 {backup_count} 个文件到 {current_backup_path}")

# ===== 清理旧备份（保留最新 KEEP_LATEST 个）=====
backup_folders = [f for f in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, f)) and f != ".git"]
backup_folders.sort(reverse=True)   # 最新的在前

deleted_count = 0
if len(backup_folders) > KEEP_LATEST:
    for folder in backup_folders[KEEP_LATEST:]:
        shutil.rmtree(os.path.join(BACKUP_DIR, folder))
        deleted_count += 1

print(f"清理了 {deleted_count} 个旧备份文件夹")

# ===== 更新状态文件和日志 =====
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"last_backup": beijing_time.isoformat()}, f)

log_entry = f"[{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}] 备份成功: 增加 {backup_count} 文件 | 清理 {deleted_count} 旧文件夹\n"
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print(f"✅ 备份任务圆满完成: {timestamp}")
