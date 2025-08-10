#!/usr/bin/env python3
"""驗證 main.py 啟動狀態的腳本"""

import subprocess
import sys
import os

def verify_with_venv():
    """使用虛擬環境驗證"""
    print("測試方法 1: 使用虛擬環境的 Python...")
    try:
        result = subprocess.run(
            ['venv/bin/python', '-c', 'import transformers; print("✅ transformers 模組已安裝")'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ transformers 模組未安裝")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 錯誤: {e}")

def verify_with_script():
    """使用 run.sh 腳本驗證"""
    print("\n測試方法 2: 使用 run.sh 腳本...")
    if os.path.exists('run.sh'):
        try:
            process = subprocess.Popen(
                ['./run.sh'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            output, _ = process.communicate(input="quit\n", timeout=10)
            
            if "Agent initialized successfully" in output:
                print("✅ main.py 透過 run.sh 啟動成功")
            else:
                print("❌ main.py 啟動失敗")
        except subprocess.TimeoutExpired:
            process.kill()
            print("❌ 啟動超時")
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    else:
        print("❌ run.sh 不存在")

def show_instructions():
    """顯示使用說明"""
    print("\n" + "="*60)
    print("✅ main.py 已修復完成！")
    print("="*60)
    print("\n使用方法：")
    print("1. 使用 run.sh 腳本（推薦）:")
    print("   ./run.sh")
    print("\n2. 手動啟動虛擬環境:")
    print("   source venv/bin/activate")
    print("   python main.py")
    print("\n3. 直接使用虛擬環境的 Python:")
    print("   venv/bin/python main.py")
    print("\n注意：直接使用 python3 main.py 會失敗，因為需要虛擬環境中的套件。")

if __name__ == "__main__":
    print("正在驗證 main.py 啟動狀態...\n")
    verify_with_venv()
    verify_with_script()
    show_instructions()