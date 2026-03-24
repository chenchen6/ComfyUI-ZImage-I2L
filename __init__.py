import os
import sys
import subprocess
import importlib.util

def check_and_install():
    current_dir = os.path.dirname(__file__)
    diffsynth_path = os.path.join(current_dir, "DiffSynth-Studio")
    req_path = os.path.join(current_dir, "requirements.txt")

    # 1. 自動 Clone 核心庫
    if not os.path.exists(diffsynth_path):
        print(f"[Z-Image] 正在下載 DiffSynth-Studio 核心庫...")
        try:
            subprocess.check_call(["git", "clone", "https://github.com/modelscope/DiffSynth-Studio.git", diffsynth_path])
        except Exception as e:
            print(f"[Z-Image] Git Clone 失敗: {e}")

    # 2. 自動安裝 requirements.txt 中的依賴
    if os.path.exists(req_path):
        try:
            # 簡單檢查 modelscope 是否已安裝，避免每次啟動都掃描
            if importlib.util.find_spec("modelscope") is None:
                print(f"[Z-Image] 正在安裝必要環境依賴...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        except Exception as e:
            print(f"[Z-Image] 依賴安裝失敗: {e}")

    # 3. 路徑映射 (核心關鍵)
    if diffsynth_path not in sys.path:
        sys.path.insert(0, diffsynth_path)

# 執行初始化
check_and_install()

# 匯入節點映射
try:
    from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError as e:
    print(f"[Z-Image] 載入 nodes.py 失敗: {e}")
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']