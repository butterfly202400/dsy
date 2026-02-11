import os
import shutil
import datetime
import time

# ===== 配置 =====
BACKUP_DIR = "backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")
KEEP_DAYS = 15  # 保留天数

# 创建备份目录
os.makedirs(BACKUP_DIR, exist_ok=True)

# 获取北京时间
beijing_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
timestamp = beijing_time.strftime("%Y-%m-%d_%H-%M-%S")

# 创建本次备份文件夹
current_backup_path = os.path.join(BACKUP_DIR, timestamp)
os.makedirs(current_backup_path, exist_ok=True)

backup_count = 0

# ===== 备份 txt 和 m3u 文件（仅根目录）=====
for file in os.listdir("."):
    if file.endswith(".txt") or file.endswith(".m3u"):
        if file == "backup_log.txt":
            continue
        shutil.copy2(file, current_backup_path)
        backup_count += 1

# ===== 清理15天前备份 =====
now = time.time()
deleted_count = 0

for folder in os.listdir(BACKUP_DIR):
    folder_path = os.path.join(BACKUP_DIR, folder)

    if os.path.isdir(folder_path):
        folder_time = os.path.getmtime(folder_path)
        days_old = (now - folder_time) / 86400

        if days_old > KEEP_DAYS:
            shutil.rmtree(folder_path)
            deleted_count += 1

# ===== 写入日志 =====
log_entry = (
    f"时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} | "
    f"备份文件数: {backup_count} | "
    f"清理旧备份: {deleted_count}\n"
)

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print("备份完成")
