# scripts/demo/main.py
import requests
import time

def main():
    response = requests.get('https://api.github.com')
    print("Response Test")
    print("Response Response - ", response.json())
    # print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Response Test")
    # print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Response Response - {response.json()}")

if __name__ == "__main__":
    main()
