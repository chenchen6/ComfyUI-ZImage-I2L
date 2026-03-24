# ComfyUI-ZImage-I2L
image to lora for z-image-turbo in ComfyUI

參考
DiffSynth-Studio https://github.com/modelscope/DiffSynth-Studio

## Installation 安裝方式
Clone this repository into your ComfyUI custom nodes folder:
```
cd ComfyUI/custom_nodes
git clone https://github.com/chenchen6/ComfyUI-ZImage-I2L.git



## MODEL's location 模型存放位置
The directory structure after download:
```
    ~/models/
    ├── Tongyi-MAI/
    │   ├── Z-Image/
    │   │   └── transformer/*.safetensors
    │   └── Z-Image-Turbo/
    │       ├── text_encoder/*.safetensors
    │       ├── vae/diffusion_pytorch_model.safetensors
    │       └── tokenizer/
    └── DiffSynth-Studio/
        ├── General-Image-Encoders/
        │   ├── SigLIP2-G384/model.safetensors
        │   └── DINOv3-7B/model.safetensors
        └── Z-Image-i2L/
            └── model.safetensors
