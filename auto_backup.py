import os
import shutil
from datetime import datetime, timedelta, timezone

# ==============================
# 北京时间 UTC+8
# ==============================
beijing_tz = timezone(timedelta(hours=8))
now = datetime.now(beijing_tz)
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_ROOT = os.path.join(ROOT_DIR, "backup")
BACKUP_DIR = os.path.join(BACKUP_ROOT, timestamp)
LOG_FILE = os.path.join(BACKUP_ROOT, "backup_log.txt")

os.makedirs(BACKUP_DIR, exist_ok=True)

backup_count = 0

# ==============================
# 备份 .txt 和 .m3u 文件
# ==============================
for filename in os.listdir(ROOT_DIR):
    filepath = os.path.join(ROOT_DIR, filename)

    if os.path.isfile(filepath) and (
        filename.endswith(".txt") or filename.endswith(".m3u")
    ):
        shutil.copy2(filepath, os.path.join(BACKUP_DIR, filename))
        backup_count += 1

# ==============================
# 只保留最近10份备份
# ==============================
folders = [
    f for f in os.listdir(BACKUP_ROOT)
    if os.path.isdir(os.path.join(BACKUP_ROOT, f))
]

folders.sort(reverse=True)

if len(folders) > 10:
    for old_folder in folders[10:]:
        shutil.rmtree(os.path.join(BACKUP_ROOT, old_folder))

# ==============================
# 写日志
# ==============================
log_entry = (
    f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')} | "
    f"备份文件数: {backup_count}\n"
)

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print("备份完成")
print(log_entry)
