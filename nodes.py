import uuid
import os
import gc
import torch
import numpy as np
from PIL import Image
import folder_paths
import comfy.sd
import comfy.utils
from safetensors.torch import save_file
from comfy import model_management as mm

os.environ["MODELSCOPE_CACHE"] = folder_paths.models_dir

try:
    from diffsynth.pipelines.z_image import (
        ZImagePipeline, ModelConfig,
        ZImageUnit_Image2LoRAEncode, ZImageUnit_Image2LoRADecode
    )
    DIFFSYNTH_AVAILABLE = True
except ImportError:
    DIFFSYNTH_AVAILABLE = False
    print("\n[Z-Image] 錯誤：找不到 DiffSynth 庫！請確保已安裝 diffsynth-studio。\n")

# ==========================================
# 1. 載入器：處理 Transformer + Turbo Tokenizer 混用
# ==========================================
class ZImage_I2L_Loader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "precision": (["bfloat16", "float16"], {"default": "bfloat16"}),
            }
        }

    RETURN_TYPES = ("ZIMAGE_PIPE",)
    RETURN_NAMES = ("pipeline",)
    FUNCTION = "load_pipeline"
    CATEGORY = "Z-Image"

    def load_pipeline(self, precision):
        if not DIFFSYNTH_AVAILABLE:
            raise Exception("❌ DiffSynth 未安裝")

        dtype = torch.bfloat16 if precision == "bfloat16" else torch.float16
        
        # 載入前清理顯存
        mm.unload_all_models()
        gc.collect()
        torch.cuda.empty_cache()

        vram_config = {
            "offload_dtype": dtype, "offload_device": "cpu",
            "onload_dtype": dtype, "onload_device": "cuda",
            "preparing_dtype": dtype, "preparing_device": "cuda",
            "computation_dtype": dtype, "computation_device": "cuda",
        }

        print(f"\n[Z-Image] 正在從本地目錄載入模型架構: {folder_paths.models_dir}")

        # 這裡會自動對應到 models/Tongyi-MAI/Z-Image... 等路徑
        pipe = ZImagePipeline.from_pretrained(
            torch_dtype=dtype,
            device="cuda",
            model_configs=[
                # 使用原版 Z-Image 的 Transformer
                ModelConfig(model_id="Tongyi-MAI/Z-Image", origin_file_pattern="transformer/*.safetensors", **vram_config),
                # 使用 Turbo 版的 Text Encoder 與 VAE
                ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="text_encoder/*.safetensors", **vram_config),
                ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="vae/diffusion_pytorch_model.safetensors", **vram_config),
                # 官方通用編碼器
                ModelConfig(model_id="DiffSynth-Studio/General-Image-Encoders", origin_file_pattern="SigLIP2-G384/model.safetensors", **vram_config),
                ModelConfig(model_id="DiffSynth-Studio/General-Image-Encoders", origin_file_pattern="DINOv3-7B/model.safetensors", **vram_config),
                ModelConfig(model_id="DiffSynth-Studio/Z-Image-i2L", origin_file_pattern="model.safetensors", **vram_config),
            ],
            # 關鍵配置：指定使用 Turbo 的 Tokenizer
            tokenizer_config=ModelConfig(model_id="Tongyi-MAI/Z-Image-Turbo", origin_file_pattern="tokenizer/"),
            vram_limit=torch.cuda.mem_get_info("cuda")[1] / (1024 ** 3) - 2.0,
        )
        
        print("✅ [Z-Image] Pipeline 載入完成！")
        return (pipe,)

# ==========================================
# 2. 生成器：將圖片轉化為 LoRA 權重並存檔
# ==========================================
class ZImage_I2L_Generator:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pipeline": ("ZIMAGE_PIPE",),
                "images": ("IMAGE",),
                "lora_name": ("STRING", {"default": "zimage_lora"}),
            }
        }

    RETURN_TYPES = ("STRING", "LORA_PATH")
    RETURN_NAMES = ("lora_name", "full_path")
    FUNCTION = "generate"
    CATEGORY = "Z-Image"

    def generate(self, pipeline, images, lora_name):
        if pipeline is None:
            raise ValueError("❌ Pipeline 未初始化")

        # 轉換圖片格式
        pil_images = []
        for img in images:
            curr_img = img.squeeze() if len(img.shape) == 4 else img
            i = 255. * curr_img.cpu().numpy()
            pil_images.append(Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)).convert("RGB"))
        
        print(f"🎨 [Z-Image] 正在編碼 {len(pil_images)} 張圖片並提取風格...")

        with torch.no_grad():
            embs = ZImageUnit_Image2LoRAEncode().process(pipeline, image2lora_images=pil_images)
            lora_data = ZImageUnit_Image2LoRADecode().process(pipeline, **embs)["lora"]
        
        # 產生唯一檔名並存檔到 models/loras
        file_uuid = uuid.uuid4().hex[:4]
        file_name = f"{lora_name}_{file_uuid}.safetensors"
        save_path = os.path.join(folder_paths.models_dir, "loras", file_name)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        save_file(lora_data, save_path)

        print(f"💾 [Z-Image] LoRA 已即時儲存至: {save_path}")
        return (file_name, save_path)

# ==========================================
# 3. 套用器：免重新整理，直接從路徑載入 LoRA
# ==========================================
class ZImage_Lora_Apply:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_path": ("LORA_PATH", {"forceInput": True}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "apply_lora"
    CATEGORY = "Z-Image"

    def apply_lora(self, model, clip, lora_path, strength_model, strength_clip):
        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        if not os.path.exists(lora_path):
            print(f"❌ 檔案路徑不存在: {lora_path}")
            return (model, clip)

        # 直接讀取檔案並 Patch 到模型上
        print(f"📥 [Z-Image] 正在即時掛載動態 LoRA: {os.path.basename(lora_path)}")
        lora_weights = comfy.utils.load_torch_file(lora_path, safe_load=True)
        
        model_lora, clip_lora = comfy.sd.load_lora_for_models(
            model, clip, lora_weights, strength_model, strength_clip
        )

        return (model_lora, clip_lora)

# --- 註冊節點 ---
NODE_CLASS_MAPPINGS = {
    "ZImage_I2L_Loader": ZImage_I2L_Loader,
    "ZImage_I2L_Generator": ZImage_I2L_Generator,
    "ZImage_Lora_Apply": ZImage_Lora_Apply,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZImage_I2L_Loader": "Z-Image Pipeline Loader",
    "ZImage_I2L_Generator": "Z-Image Image-to-LoRA",
    "ZImage_Lora_Apply": "Z-Image LoRA Apply (Instant)",
}