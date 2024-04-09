# DyberAIGenshin-VITS
DyberPet_GenshinImpact + KimiChat + BertVITS2

## Usage
### Environment
```bash
conda create -n pet python=3.9
conda activate pet
conda install -c conda-forge apscheduler --yes
conda install -c conda-forge pynput --yes
conda install -c conda-forge pywin32 --yes
pip install -r requirements.txt
```

### Download
```bash
git clone git@gitee.com:MuGeminorum/DyberPet.git
cd DyberPet
```

### Run
```bash
python run_DyberPet.py
```

## Thanks
- [DyberPet](https://github.com/ChaozhongLiu/DyberPet)
- [DyberPet_GenshinImpact](https://github.com/ChaozhongLiu/DyberPet_GenshinImpact)
- [KimiChat](https://platform.moonshot.cn/docs/api-reference)
- [Bert-VITS2](https://github.com/fishaudio/Bert-VITS2)
- [Bert-VITS2_Genshin_TTS](https://www.modelscope.cn/studios/erythrocyte/Bert-VITS2_Genshin_TTS)