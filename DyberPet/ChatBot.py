import os
import json
from openai import OpenAI
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QThread
from BertVITS2.VITS import TTS
from DyberPet import settings


class Speaker(QThread):
    finished = Signal(name="speaker_finished")

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

    def _get_answer(self):
        self.history += [{"role": "user", "content": self.query}]
        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=self.history,
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        self.history += [{"role": "assistant", "content": result}]
        return result

    def _test_answer(self):
        result = "当前是测试用文案，用于绕过大语言模型直接测试语音合成模块！" * 5
        self.history += [{"role": "user", "content": self.query}]
        return result

    def run(self):
        self._clean_cache()
        if not self.speaking:
            self.finished.emit()
            return

        result = self._test_answer()
        if not self.speaking:
            self.finished.emit()
            return

        audio_path, audio_duration = self.tts.speech(
            content=result, speaker=settings.petname
        )

        if self.speaking:
            self.answer.emit(result, audio_path, audio_duration)
        else:
            self.finished.emit()

    def speak(
        self,
        history: list,
        query: str,
    ):
        self.query = query
        self.history = history
        self.speaking = True
        self.start()

    def stop(self):
        self.speaking = False


class ChatBot(QWidget):
    answer = Signal(str, str, int, name="answer_sig")
    interrupted = Signal(name="interrupt_sig")

    def __init__(self, parent=None):
        super(ChatBot, self).__init__(parent)
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.initPrompt()
        self.tts = TTS()
        self.speaker = Speaker(self.client, self.tts, self.answer)
        self.__connectSignalToSlot()

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

    def __connectSignalToSlot(self):
        self.speaker.finished.connect(self._interrupted)

    def chat(self, query):
        self.tts.stopping = False
        print(self.history)
        self.speaker.speak(self.history, query)

    def interrupt(self):
        self.tts.stopping = True
        if self.speaker and self.speaker.isRunning():
            self.speaker.stop()
        else:
            self._interrupted()

    # slot
    def _interrupted(self):
        self.interrupted.emit()
