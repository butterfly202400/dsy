import os
import shutil
import datetime
import json

# ===== 配置 =====
BACKUP_DIR = "backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")
STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.json")
KEEP_LATEST = 15
INTERVAL_HOURS = 70 

os.makedirs(BACKUP_DIR, exist_ok=True)

# 获取当前北京时间
beijing_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

# ===== 检查是否满足备份周期 =====
last_backup_time = None
diff_hours = 999.0  # 初始设为一个较大的值，确保第一次运行能成功

if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_backup_time = datetime.datetime.fromisoformat(data["last_backup"])
            # 统一时区进行计算
            diff_hours = (beijing_time - last_backup_time).total_seconds() / 3600
    except Exception as e:
        print(f"状态文件读取失败或格式不正确，将执行强制备份。错误: {e}")

# 检查间隔
if last_backup_time and diff_hours < INTERVAL_HOURS:
    print(f"检查时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前间隔: {diff_hours:.1f} 小时，不满 {INTERVAL_HOURS} 小时。")
    print(">>> 此次跳过备份。")
    exit(0)

print(f"开始备份：距离上次已过 {diff_hours:.1f} 小时 (或首次备份)...")

# ===== 执行备份任务 =====
timestamp = beijing_time.strftime("%Y-%m-%d_%H-%M-%S")
current_backup_path = os.path.join(BACKUP_DIR, timestamp)
os.makedirs(current_backup_path, exist_ok=True)

backup_count = 0
for file in os.listdir("."):
    if (file.endswith(".txt") or file.endswith(".m3u")) and os.path.isfile(file):
        if file == "backup_log.txt": continue
        shutil.copy2(file, current_backup_path)
        backup_count += 1

# ===== 清理旧备份 =====
backup_folders = [f for f in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, f)) and f != ".git"]
backup_folders.sort(reverse=True)

deleted_count = 0
if len(backup_folders) > KEEP_LATEST:
    for folder in backup_folders[KEEP_LATEST:]:
        shutil.rmtree(os.path.join(BACKUP_DIR, folder))
        deleted_count += 1

# ===== 更新状态和日志 =====
with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"last_backup": beijing_time.isoformat()}, f)

log_entry = f"[{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}] 备份成功: 增加 {backup_count} 文件 | 清理 {deleted_count} 旧文件夹\n"
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(log_entry)

print(f"备份任务圆满完成: {timestamp}")
