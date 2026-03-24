# ComfyUI-ZImage-I2L
image to lora for z-image-turbo in ComfyUI

參考
DiffSynth-Studio https://github.com/modelscope/DiffSynth-Studio

## Installation 安裝方式
Clone this repository into your ComfyUI custom nodes folder:
```
cd ComfyUI/custom_nodes
git clone https://github.com/chenchen6/ComfyUI-ZImage-I2L.git
```
```
cd ComfyUI/ComfyUI-ZImage-I2L
pip install -r requirements.txt
```
## NODE
| node | description|
| :--- | :--- |
| Z-Image Pipeline Loader |load Z-Image Image-to-LoRA pipeline|
| Z-Image Image-to-LoRA |main node for training lora|
| Z-Image LoRA Apply (Instant) |replace the original lora model|

!!If "Z-Image LoRA Apply (Instant)" doesn't work, disconnect the pipeline, and change to original one.

## MODEL
Models will be automatically downloaded from ModelScope on first run
Or downloaded from Huggingface before run the workflow
* recommend downloading from huggingface if not in China region

Download links from Huggingface
[Tongyi-MAI/Z-Image/transformer](https://huggingface.co/Tongyi-MAI/Z-Image/tree/main/transformer)
[Tongyi-MAI/Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/tree/main/)
[DiffSynth-Studio/General-Image-Encoders](https://huggingface.co/DiffSynth-Studio/General-Image-Encoders/tree/main)
[DiffSynth-Studio/Z-Image-i2L](https://huggingface.co/DiffSynth-Studio/Z-Image-i2L/tree/main)


## MODEL's location 模型存放位置
The directory structure after download:
```
    ~/models/
    ├── Tongyi-MAI/
    │   ├── Z-Image/
    │   │   └── transformer/.safetensors, json
    │   └── Z-Image-Turbo/
    │       ├── text_encoder/.safetensors, json
    │       ├── vae/diffusion_pytorch_model.safetensors, json
    │       └── tokenizer/josn, txt
    └── DiffSynth-Studio/
        ├── General-Image-Encoders/
        │   ├── SigLIP2-G384/model.safetensors
        │   └── DINOv3-7B/model.safetensors
        └── Z-Image-i2L/
            └── model.safetensors
```
## EXSAMPLE WORKFLOW
4 image to train lora (lora_name: zimage_lora). Export into models/loras folder
