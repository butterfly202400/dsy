import os
import shutil
import datetime
import json

# ===== 配置 =====
BACKUP_DIR = "backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")
STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.json")
KEEP_LATEST = 15
INTERVAL_HOURS = 72  # 精确72小时

os.makedirs(BACKUP_DIR, exist_ok=True)

# 当前北京时间
beijing_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)

# ===== 检查是否满足72小时 =====
last_backup_time = None

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        last_backup_time = datetime.datetime.fromisoformat(data["last_backup"])

if last_backup_time:
    diff_hours = (beijing_time - last_backup_time).total_seconds() / 3600
    if diff_hours < INTERVAL_HOURS:
        print("未满72小时，跳过备份")
        exit(0)

# ===== 开始备份 =====
timestamp = beijing_time.strftime("%Y-%m-%d_%H-%M-%S")
current_backup_path = os.path.join(BACKUP_DIR, timestamp)
os.makedirs(current_backup_path, exist_ok=True)

backup_count = 0

for file in os.listdir("."):
    if file.endswith(".txt") or file.endswith(".m3u"):
        if file == "backup_log.txt":
            continue
        shutil.copy2(file, current_backup_path)
        backup_count += 1

# ===== 只保留最新15份 =====
deleted_count = 0

backup_folders = [
    f for f in os.listdir(BACKUP_DIR)
    if os.path.isdir(os.path.join(BACKUP_DIR, f))
]

backup_folders.sort(reverse=True)

if len(backup_folders) > KEEP_LATEST:
    for folder in backup_folders[KEEP_LATEST:]:
        shutil.rmtree(os.path.join(BACKUP_DIR, folder))
        deleted_count += 1

# ===== 更新状态文件 =====
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"last_backup": beijing_time.isoformat()}, f)

# ===== 写日志 =====
log_entry = (
    f"时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} | "
    f"备份文件数: {backup_count} | "
    f"删除旧备份: {deleted_count}\n"
)

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print("备份完成")
