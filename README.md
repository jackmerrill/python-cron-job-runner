# Python Cron Job Runner

A Docker-based application for managing and running Python scripts using cron-like scheduling.

## Project Structure
```
.
├── localbin/
│   ├── app.py          # Main scheduler application
│   ├── check_heartbeat.py # Heartbeat monitoring script
│   ├── entrypoint.sh   # Docker entrypoint script
│   └── requirements.txt # Python dependencies
├── scripts/            # Directory for your Python scripts
├── log/               # Directory for logs
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## Features

- Automatically manages Python virtual environments for each script
- Cron-like scheduling for Python scripts
- Isolated environments for different scripts
- Automatic dependency installation from requirements.txt
- Comprehensive logging system with heartbeat monitoring
- Docker containerized for easy deployment
- Host timezone synchronization

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation & Running

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <project-directory>
```

2. Add your Python scripts:
   - Create a directory under `scripts/` for each script project
   - Each project directory should contain:
     - `main.py` - Your main Python script
     - `requirements.txt` - Python dependencies
     - `config` - Cron schedule configuration (format: `second minute hour day month day_of_week`)

3. Start the application using Docker Compose:
```bash
docker-compose up -d
```

## Configuration

### Cron Configuration Format
The `config` file uses standard cron format with seconds:
```
second minute hour day month day_of_week
```

Valid formats:
- Standard values (e.g., `0 0 13 * * *` runs at 13:00:00 daily)
- Asterisk `*` for any value
- All zeros (`0 0 0 0 0 0`) to disable the task

Field constraints:
- second: 0-59
- minute: 0-59
- hour: 0-23
- day: 1-31
- month: 1-12
- day_of_week: 0-6 (0 is Sunday)

Examples:
```
0 0 13 * * *    # Runs at 13:00:00 every day
0 */30 * * * *  # Runs every 30 minutes
0 0 0 0 0 0     # Task disabled
```

### Script Project Structure
Each script project should be organized as follows:
```
scripts/
└── your-script-name/
    ├── main.py         # Your main Python script
    ├── requirements.txt # Project dependencies
    └── config          # Cron schedule configuration
```

### System Configuration
- Logs directory: `/log/`
- Scripts directory: `/scripts/`
- Virtual environments: `/proj-venv/`
- Timezone: Synced with host system

## Monitoring

The application includes a heartbeat monitoring system that:
- Writes heartbeat status every minute
- Logs all script execution results
- Maintains separate log files for each script

### Log Files
- Main application logs: `/log/log.txt`
- Heartbeat status: `/log/heartbeat.txt`
- Script-specific logs: `/log/<script-name>/log.txt`

You can check logs using:
```bash
docker exec daily-run-zwpride cat /log/demo1/log.txt
```

## Example Project

### Demo Script Structure
```
scripts/
└── demo1/              # Example project that tests GitHub API
    ├── main.py         # Script to call GitHub API
    ├── requirements.txt # Only needs 'requests' package
    └── config          # Runs daily at 13:00
```

### Example Files

1. `main.py` - A simple script that calls GitHub API:
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

2. `requirements.txt` - Dependencies:
```
requests
```

3. `config` - Cron schedule (runs every day at 13:00):
```
0 0 13 * * *
```

### Output

The script will:
- Make a request to GitHub's API
- Log the timestamp and response
- Store all output in `/log/demo1/log.txt`

## Docker Configuration

### Dockerfile
- Base image: Ubuntu 24.04
- Python environment: Python 3 with venv support
- Automatic dependency installation
- Non-interactive installation mode

### Docker Compose
- Container name: daily-run-zwpride
- Automatic restart policy: unless-stopped
- Volume mappings:
  - `./log:/log` - Script execution and heartbeat logs
  - `./scripts:/scripts` - Python scripts directory
  - `proj-venv:/proj-venv` - Persistent Python virtual environments
  - `/etc/localtime:/etc/localtime:ro` - Host timezone synchronization



