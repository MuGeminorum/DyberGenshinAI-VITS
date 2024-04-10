import os
import json
from openai import OpenAI
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QThread
from BertVITS2.VITS import TTS
from DyberPet import settings


class Speaker(QThread):
    def __init__(
        self,
        client: OpenAI,
        tts: TTS,
        answer: Signal,
        parent=None,
    ):
        super().__init__(parent)
        self.client = client
        self.answer = answer
        self.tts = tts
        self.speaking = True

    def _clean_cache(self, folder_path="data"):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.lower().endswith(".wav"):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"删除文件 {file_path} 时出错: {e.strerror}")

    def run(self):
        self._clean_cache()
        self.history += [{"role": "user", "content": self.query}]
        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=self.history,
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        self.history += [{"role": "assistant", "content": result}]
        audio_path = self.tts.speech(content=result, speaker=settings.petname)
        if self.speaking:
            self.answer.emit(result, audio_path)

    def speak(
        self,
        history: list,
        query: str,
    ):
        self.query = query
        self.history = history
        self.speaking = True
        self.start()

    def shutup(self):
        self.speaking = False
        self.terminate()


class Test(QThread):
    def __init__(
        self,
        client: OpenAI,
        tts: TTS,
        answer: Signal,
        parent=None,
    ):
        super().__init__(parent)
        self.client = client
        self.answer = answer
        self.tts = tts
        self.speaking = True

    def _clean_cache(self, folder_path="data"):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.lower().endswith(".wav"):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"删除文件 {file_path} 时出错: {e.strerror}")

    def run(self):
        self._clean_cache()
        result = "当前是测试用文案，用于绕过大语言模型直接测试语音合成模块！" * 5
        self.history += [{"role": "user", "content": self.query}]
        audio_path = self.tts.speech(content=result, speaker=settings.petname)
        if self.speaking:
            self.answer.emit(result, audio_path)

    def speak(
        self,
        history: list,
        query: str,
    ):
        self.query = query
        self.history = history
        self.speaking = True
        self.start()

    def shutup(self):
        self.speaking = False
        self.terminate()


class ChatBot(QWidget):
    answer = Signal(str, str, name="answer_sig")
    interrupted = Signal(bool, name="interrupt_sig")

    def __init__(self, parent=None):
        super(ChatBot, self).__init__(parent)
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.initPrompt()
        self.tts = TTS(self)
        self.worker = Test(self.client, self.tts, self.answer, parent=self)

    def initPrompt(self):
        petCfg = json.load(
            open(
                os.path.join(
                    settings.BASEDIR, "res/role", settings.petname, "pet_conf.json"
                ),
                "r",
                encoding="UTF-8",
            )
        )
        self.history = [
            {
                "role": "system",
                "content": petCfg["prompt"] if "prompt" in petCfg else "",
            },
        ]

    def chat(self, query):
        print(self.history)
        self.worker.speak(self.history, query)

    def interrupt(self):
        if self.worker and self.worker.isRunning():
            self.worker.shutup()

        self.initPrompt()
        self.interrupted.emit(True)
