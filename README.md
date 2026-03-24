# ComfyUI-ZImage-I2L
image to lora for z-image-turbo in ComfyUI

參考
DiffSynth-Studio https://github.com/modelscope/DiffSynth-Studio


MODEL's location模型存放位置
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
    ```
