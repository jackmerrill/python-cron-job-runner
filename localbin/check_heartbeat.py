import os
import datetime
import sys

def check_heartbeat(max_minutes=5):
    """检查心跳状态
    
    Args:
        max_minutes (int): 允许的最大心跳间隔（分钟）
        
    Returns:
        bool: True 表示正常，False 表示异常
    """
    heartbeat_file = "./log/heartbeat.txt"
    
    if not os.path.exists(heartbeat_file):
        print("Heartbeat file not found")
        return False
        
    try:
        with open(heartbeat_file, "r") as f:
            last_heartbeat = datetime.datetime.strptime(
                f.read().strip(),
                "%Y-%m-%d %H:%M:%S"
            )
        
        now = datetime.datetime.now()
        diff = now - last_heartbeat
        
        if diff.total_seconds() > max_minutes * 60:
            print(f"Heartbeat too old: {diff.total_seconds() / 60:.1f} minutes")
            return False
            
        print(f"Heartbeat OK: {diff.total_seconds() / 60:.1f} minutes ago")
        return True
        
    except Exception as e:
        print(f"Error checking heartbeat: {e}")
        return False

if __name__ == "__main__":
    # 退出码：0 表示正常，1 表示异常
    sys.exit(0 if check_heartbeat() else 1) 