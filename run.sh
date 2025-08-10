#!/bin/bash
# 自動啟動虛擬環境並運行 main.py

# 啟動虛擬環境
source venv/bin/activate

# 執行 main.py
python main.py "$@"