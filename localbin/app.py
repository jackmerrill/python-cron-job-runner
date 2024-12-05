from apscheduler.schedulers.blocking import BlockingScheduler
import os
import subprocess
import logging
import time
import shutil
import datetime

PROJ_ENV_DIR = "/proj-venv"
LOG_DIR = "/log"

# 获取当前文件的绝对路径
current_path = os.path.abspath(__file__)
# 获取当前文件所在目录
current_dir = os.path.dirname(current_path)

# 设置日志文件
logging.basicConfig(
    filename=os.path.join(LOG_DIR,"log.txt"), 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.Formatter.converter = time.localtime  # 使用系统本地时间

def validate_cron_format(cron_str):
    try:
        parts = cron_str.split()
        if len(parts) != 6:
            raise ValueError(f"Expected 6 parts in cron expression, got {len(parts)}")
        
        # 更详细的验证
        second, minute, hour, day, month, day_of_week = parts
        
        # 检查是否全为0（禁用标记）
        if all(part == "0" for part in parts):
            return True

        # 验证范围（对于非*的值）
        def validate_field(value, min_val, max_val, name):
            if value == '*':
                return
            try:
                val = int(value)
                if not (min_val <= val <= max_val):
                    raise ValueError(f"Invalid {name} value: {value}, should be between {min_val} and {max_val}")
            except ValueError as e:
                raise ValueError(f"Invalid {name} format: {value}")

        validate_field(second, 0, 59, "second")
        validate_field(minute, 0, 59, "minute")
        validate_field(hour, 0, 23, "hour")
        validate_field(day, 1, 31, "day")
        validate_field(month, 1, 12, "month")
        validate_field(day_of_week, 0, 6, "day_of_week")
        
        return True
    except Exception as e:
        raise ValueError(f"Cron format validation failed: {str(e)}")

def read_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config = file.read().strip()
            
            # 检查是否为关闭标记
            if config == "0 0 0 0 0 0":
                logging.info(f"Task in {config_path} is explicitly disabled")
                return None
                
            # 验证 cron 格式
            try:
                validate_cron_format(config)
            except ValueError as e:
                logging.error(f"Invalid config in {config_path}: {str(e)}")
                return None
                
            return config
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error reading config {config_path}: {str(e)}")
        return None

def execute_script(script_path, env_path, log_path):
    activate_script = os.path.join(env_path, 'bin', 'activate')
    if os.path.exists(script_path) and os.path.exists(activate_script):
        # 添加超时控制
        timeout = 3600  # 1小时
        cmd = f"/bin/bash -c 'source {activate_script} && python {script_path} | while IFS= read -r line; do echo \"$(date \"+%Y-%m-%d %H:%M:%S\") - $line\" >> {log_path}; done 2>&1'"
        try:
            subprocess.run(cmd, shell=True, check=True, timeout=timeout)
            logging.info(f"Executed {script_path} successfully.")
        except subprocess.TimeoutExpired:
            logging.error(f"Script {script_path} timed out after {timeout} seconds")
        except Exception as e:
            logging.error(f"Error executing {script_path}: {str(e)}")
    else:
        logging.error(f"Environment or main script not found for {script_path}")

def write_heartbeat():
    """写入心跳信息到文件"""
    try:
        heartbeat_file = os.path.join(LOG_DIR, "heartbeat.txt")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(heartbeat_file, "w") as f:
            f.write(current_time)
        logging.debug(f"Heartbeat updated at {current_time}")
    except Exception as e:
        logging.error(f"Failed to write heartbeat: {e}")

def schedule_tasks(base_dir):
    scheduler = BlockingScheduler()
    
    # 添加心跳任务，每分钟执行一次
    scheduler.add_job(
        write_heartbeat,
        'interval',
        minutes=1,
        id='heartbeat'
    )
    
    tasks_status = []  # 记录所有任务的状态
    
    # 不存在时，创建 env 目录
    os.makedirs(PROJ_ENV_DIR, exist_ok=True)
    # 检查当前的 env 有哪些
    not_used_venvs = {venv for venv in os.listdir(PROJ_ENV_DIR)}
    
    for proj in os.listdir(base_dir):
        proj_path = os.path.join(base_dir, proj)
        if os.path.isdir(proj_path):
            status = {
                "project": proj,
                "status": "unknown",
                "message": ""
            }
            
            config_file = os.path.join(proj_path, 'config')
            env_path = os.path.join(PROJ_ENV_DIR, proj)
            main_script = os.path.join(proj_path, 'main.py')
            log_dir_path = os.path.join(LOG_DIR, proj)
            os.makedirs(log_dir_path, exist_ok=True)
            log_path = os.path.join(log_dir_path, "log.txt")

            # 处理虚拟环境
            if not os.path.exists(env_path):
                try:
                    # 创建 venv
                    create_venv_cmd = f"/bin/bash -c 'python3 -m venv {env_path}'"
                    instal_req_cmd = f"/bin/bash -c 'source {env_path}/bin/activate && python -m pip install -r {proj_path}/requirements.txt'"
                    subprocess.run(create_venv_cmd, shell=True, check=True)
                    logging.info(f"Created virtual environment for {proj}")
                    subprocess.run(instal_req_cmd, shell=True, check=True)
                    logging.info(f"Installed requirements for {proj}")
                except Exception as e:
                    logging.error(f"Failed to setup environment for {proj}: {e}")
                    if os.path.exists(env_path):
                        shutil.rmtree(env_path)
                    status.update({"status": "error", "message": f"Environment setup failed: {str(e)}"})
                    tasks_status.append(status)
                    continue

            not_used_venvs.discard(proj)

            # 处理配置和调度
            if os.path.exists(config_file):
                cron_schedule = read_config(config_file)
                if cron_schedule is None:
                    status.update({"status": "disabled", "message": "Task disabled or invalid config"})
                    tasks_status.append(status)
                    continue
                
                try:
                    # 读取格式为 second minute hour day month day_of_week
                    second, minute, hour, day, month, day_of_week = cron_schedule.split()
                    scheduler.add_job(
                        execute_script,
                        'cron',
                        (main_script, env_path, log_path),
                        second=second,
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week
                    )
                    status.update({"status": "scheduled", "message": f"Scheduled with cron: {cron_schedule}"})
                except Exception as e:
                    status.update({"status": "error", "message": f"Failed to schedule: {str(e)}"})
            else:
                status.update({"status": "error", "message": "Config file not found"})
            
            tasks_status.append(status)

    # 删除未使用的环境
    for proj in not_used_venvs:
        env_path = os.path.join(PROJ_ENV_DIR, proj)
        try:
            shutil.rmtree(env_path)
            logging.info(f"Removed unused environment: {proj}")
        except Exception as e:
            logging.error(f"Failed to remove environment {proj}: {e}")

    # 输出任务状态摘要
    logging.info("Tasks scheduling summary:")
    for status in tasks_status:
        logging.info(f"Project: {status['project']}, Status: {status['status']}, Message: {status['message']}")

    # 启动调度器
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler shutting down...")
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting scheduler...")
    schedule_tasks("/scripts")
