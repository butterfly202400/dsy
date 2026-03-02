import os
import shutil
import datetime
import json

# ===== 配置 (根据你的需求微调) =====
BACKUP_DIR = "backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")
STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.json")
KEEP_LATEST = 15     # 保留最近15份备份
# 设定为 70 小时（约3天），留出2小时余量应对 GitHub Actions 的启动延迟
INTERVAL_HOURS = 70 

os.makedirs(BACKUP_DIR, exist_ok=True)

# 获取当前北京时间 (兼容 Python 3.9+)
beijing_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

# ===== 检查是否满足备份周期 =====
last_backup_time = None
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 解析记录的 ISO 格式时间
            last_backup_time = datetime.datetime.fromisoformat(data["last_backup"])
    except Exception as e:
        print(f"读取状态文件出错: {e}，将尝试强制备份")

# 核心判断逻辑
if last_backup_time:
    diff_hours = (beijing_time - last_backup_time).total_seconds() / 3600
    if diff_hours < INTERVAL_HOURS:
        print(f"检查时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前间隔: {diff_hours:.1f} 小时，尚未达到 {INTERVAL_HOURS} 小时阈值。")
        print(">>> 此次跳过备份。")
        exit(0)

print(f"距离上次备份已过 {diff_hours if last_backup_time else '未知'} 小时，开始执行备份...")

# ===== 执行备份任务 =====
timestamp = beijing_time.strftime("%Y-%m-%d_%H-%M-%S")
current_backup_path = os.path.join(BACKUP_DIR, timestamp)
os.makedirs(current_backup_path, exist_ok=True)

backup_count = 0
for file in os.listdir("."):
    # 只备份特定的文件类型，且排除备份目录本身
    if (file.endswith(".txt") or file.endswith(".m3u")) and os.path.isfile(file):
        if file == "backup_log.txt":
            continue
        shutil.copy2(file, current_backup_path)
        backup_count += 1

# ===== 清理旧备份 (只保留最新 KEEP_LATEST 份) =====
backup_folders = [
    f for f in os.listdir(BACKUP_DIR)
    if os.path.isdir(os.path.join(BACKUP_DIR, f)) and f != ".git"
]
backup_folders.sort(reverse=True)

deleted_count = 0
if len(backup_folders) > KEEP_LATEST:
    for folder in backup_folders[KEEP_LATEST:]:
        shutil.rmtree(os.path.join(BACKUP_DIR, folder))
        deleted_count += 1

# ===== 更新状态文件和日志 =====
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"last_backup": beijing_time.isoformat()}, f)

log_entry = (
    f"[{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}] "
    f"备份成功: 增加 {backup_count} 文件 | 清理 {deleted_count} 旧文件夹\n"
)

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print(f"备份已完成并记录状态: {timestamp}")
