# DyberGenshinAI-VITS
[![Python application](https://github.com/MuGeminorum/DyberGenshinAI-VITS/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/MuGeminorum/DyberGenshinAI-VITS/actions/workflows/python-app.yml)

DyberPet_GenshinImpact + KimiChat + BertVITS2

![bg](https://github.com/MuGeminorum/DyberGenshinAI-VITS/assets/20459298/e03c7bf4-bb49-434d-9145-dab1622ee215)

## Usage
### Environment
Windows 10 + NVIDIA
```bash
conda create -n pet --yes --file conda.txt
conda activate pet
pip install -r requirements.txt
```

### Download
```bash
git clone git@gitee.com:MuGeminorum/DyberGenshinAI-VITS.git
cd DyberGenshinAI-VITS
```

### Run
```bash
python game.py
```

### Modules
```bash
git checkout module
```
Copy role module directories in `.\DyberGenshinAI-VITS\res\role` from `module` to `main` branch;<br>
Copy item module directories in `.\DyberGenshinAI-VITS\res\item` from `module` to `main` branch;

## Thanks
- [DyberPet](https://github.com/ChaozhongLiu/DyberPet)
- [DyberPet_GenshinImpact](https://github.com/ChaozhongLiu/DyberPet_GenshinImpact)
- [KimiChat](https://platform.moonshot.cn/docs/api-reference)
- [Bert-VITS2](https://github.com/fishaudio/Bert-VITS2)
- [Bert-VITS2_Genshin_TTS](https://www.modelscope.cn/studios/erythrocyte/Bert-VITS2_Genshin_TTS)
