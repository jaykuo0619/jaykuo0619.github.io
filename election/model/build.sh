#!/bin/sh
# 重新計算模型並組出網頁：sh model/build.sh
set -e
cd "$(dirname "$0")"
python3 model.py
python3 assemble.py
