# Python Cron 作业运行器

基于 Docker 的应用程序，用于管理和运行使用类 cron 调度的 Python 脚本。

## 项目结构
```
.
├── localbin/
│   ├── app.py          # 主调度应用程序
│   ├── check_heartbeat.py # 心跳监控脚本
│   ├── entrypoint.sh   # Docker 入口脚本
│   └── requirements.txt # Python 依赖
├── scripts/            # 您的 Python 脚本目录
├── log/               # 日志目录
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## 功能

- 自动管理每个脚本的 Python 虚拟环境
- Python 脚本的类 cron 调度
- 不同脚本的隔离环境
- 从 requirements.txt 自动安装依赖项
- 带有心跳监控的综合日志系统
- 使用 Docker 容器化，便于部署
- 主机时区同步

## 快速入门

### 先决条件

- Docker
- Docker Compose

### 安装与运行

1. 克隆仓库：
```bash
git clone <your-repository-url>
cd <project-directory>
```

2. 添加您的 Python 脚本：
   - 在 `scripts/` 下为每个脚本项目创建一个目录
   - 每个项目目录应包含：
     - `main.py` - 主要的 Python 脚本
     - `requirements.txt` - Python 依赖
     - `config` - Cron 调度配置（格式：`second minute hour day month day_of_week`）

3. 使用 Docker Compose 启动应用程序：
```bash
docker-compose up -d
```

## 配置

### Cron 配置格式
`config` 文件使用的标准 cron 格式（包含秒）：
```
second minute hour day month day_of_week
```

有效格式：
- 标准值（例如，`0 0 13 * * *` 每天 13:00:00 运行）
- 使用星号 `*` 表示任意值
- 全零（`0 0 0 0 0 0`）表示禁用任务

字段约束：
- 秒：0-59
- 分钟：0-59
- 小时：0-23
- 天：1-31
- 月：1-12
- 星期几：0-6（0 代表星期天）

示例：
```
0 0 13 * * *    # 每天 13:00:00 运行
0 */30 * * * *  # 每 30 分钟运行一次
0 0 0 0 0 0     # 禁用任务
```

### 脚本项目结构
每个脚本项目应组织如下：
```
scripts/
└── your-script-name/
    ├── main.py         # 您的主要 Python 脚本
    ├── requirements.txt # 项目依赖
    └── config          # Cron 调度配置
```

### 系统配置
- 日志目录：`/log/`
- 脚本目录：`/scripts/`
- 虚拟环境：`/proj-venv/`
- 时区：与主机系统同步

## 监控

该应用程序包括一个心跳监控系统：
- 每分钟写入心跳状态
- 记录所有脚本执行结果
- 为每个脚本维护独立日志文件

### 日志文件
- 应用程序主日志：`/log/log.txt`
- 心跳状态：`/log/heartbeat.txt`
- 脚本特定日志：`/log/<script-name>/log.txt`

您可以使用以下命令检查日志：
```bash
docker exec python-cron-job-runner cat /log/demo1/log.txt
```

## 示例项目

### 示例脚本结构
```
scripts/
└── demo1/              # 示例项目用于测试 GitHub API
    ├── main.py         # 调用 GitHub API 的脚本
    ├── requirements.txt # 仅需要 'requests' 包
    └── config          # 每天 13:00 运行
```

### 示例文件

1. `main.py` - 一个简单的调用 GitHub API 的脚本：
```python
# scripts/demo1/main.py
import requests
import time

def main():
    response = requests.get('https://api.github.com')
    print("Response Test")
    print("Response Response - ", response.json())

if __name__ == "__main__":
    main()
```

2. `requirements.txt` - 依赖：
```
requests
```

3. `config` - Cron 调度（每天 13:00 运行）：
```
0 0 13 * * *
```

### 输出

该脚本将：
- 向 GitHub 的 API 发出请求
- 记录时间戳和响应
- 将所有输出存储在 `/log/demo1/log.txt`

## Docker 配置

### Dockerfile
- 基础镜像：Ubuntu 24.04
- Python 环境：Python 3，带有 venv 支持
- 自动依赖安装
- 非交互安装模式

### Docker Compose
- 容器名称：python-cron-job-runner
- 自动重启策略：除非停止
- 卷映射：
  - `./log:/log` - 脚本执行和心跳日志
  - `./scripts:/scripts` - Python 脚本目录
  - `proj-venv:/proj-venv` - 持久化 Python 虚拟环境
  - `/etc/localtime:/etc/localtime:ro` - 主机时区同步
