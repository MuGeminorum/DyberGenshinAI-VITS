import json
from openai import OpenAI
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QThread
from BertVITS2.VITS import TTS


class Worker(QThread):
    def __init__(
        self,
        history: list,
        query: str,
        client: OpenAI,
        tts: TTS,
        answer: Signal,
        parent=None,
    ):
        super().__init__(parent)
        self.query = query
        self.history = history
        self.client = client
        self.answer = answer

    def run(self):
        self.history += [{"role": "user", "content": self.query}]
        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=self.history,
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        self.history += [{"role": "assistant", "content": result}]
        self.answer.emit(result)


class Test(QThread):
    def __init__(
        self,
        history: list,
        query: str,
        client: OpenAI,
        tts: TTS,
        answer: Signal,
        parent=None,
    ):
        super().__init__(parent)
        self.query = query
        self.history = history
        self.client = client
        self.answer = answer
        self.tts = tts

    def run(self):
        result = "这是测试用文案，当前用于绕过KIMICHAT测试VITS！"
        audio_path = self.tts.speech(result)
        self.answer.emit(result, audio_path)


class ChatBot(QWidget):
    answer = Signal(str, str, name="answer_sig")

    def __init__(self, parent=None):
        super(ChatBot, self).__init__(parent)
        with open("data/settings.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        self.client = OpenAI(
            api_key=data["api_key"],
            base_url="https://api.moonshot.cn/v1",
        )

        self.history = [
            {
                "role": "system",
                "content": "你是纳西妲，是米哈游公司旗下《原神》游戏中须弥国的神明，大家也称你为小吉祥草王或小草神，你更擅长以该角色的口吻进行中文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。你要保证所有的回答只能包含中文。",
            },
        ]

        self.tts = TTS(self)

    def chat(self, query):
        self.worker = Test(
            self.history, query, self.client, self.tts, self.answer, parent=self
        )
        self.worker.start()
