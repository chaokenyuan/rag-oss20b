#!/usr/bin/env python3
"""Test script to verify main.py startup"""

import subprocess
import sys
import time

def test_startup():
    """Test if main.py starts successfully with python3"""
    try:
        # Run main.py with quit command using venv python
        process = subprocess.Popen(
            ['venv/bin/python', 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Send quit command
        output, _ = process.communicate(input="quit\n", timeout=10)
        
        # Check if initialization was successful
        if "Agent initialized successfully" in output:
            print("✅ main.py 啟動成功！")
            print("\n輸出內容：")
            print("-" * 50)
            print(output)
            print("-" * 50)
            return True
        else:
            print("❌ main.py 啟動失敗")
            print("\n錯誤輸出：")
            print(output)
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ main.py 啟動超時")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)