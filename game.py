# coding:utf-8
import os
import sys
import DyberPet.settings as settings
from DyberPet.DyberPet import PetWidget
from DyberPet.Notification import DPNote
from DyberPet.Accessory import DPAccessory
from DyberPet.Dashboard.DashboardUI import DashboardMainWindow
from DyberPet.DyberSettings.DyberControlPanel import ControlMainWindow
from qfluentwidgets import FluentTranslator
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLocale
from tendo import singleton
from sys import platform


StyleSheet = f"""
#PetTM {{
    font-family: "Segoe UI";
    border: 1px solid #08060f;
    border-radius: 7px;
}}
#PetTM::chunk {{
    background-color: #ef4e50;
    border-radius: 5px;
}}
#PetFC {{
    font-family: "Segoe UI";
    border: 1px solid #08060f;
    border-radius: 7px;
}}
#PetFC::chunk {{
    background-color: #47c0d2;
    border-radius: 5px;
}}
"""
# For translation:
# pylupdate5 langs.pro
# lrelease langs.zh_CN.ts

# For .exe:
# Now we use pyinstaller 6.5.0
# pyinstaller --noconsole --hidden-import="pynput.mouse._win32" --hidden-import="pynput.keyboard._win32" run_DyberPet.py


class DyberPetApp(QApplication):
    def __init__(self, *args, **kwargs):
        super(DyberPetApp, self).__init__(*args, **kwargs)
        # Connect the signal to a slot
        self.setStyleSheet(StyleSheet)
        self.setQuitOnLastWindowClosed(False)
        screens = self.screens()
        # internationalization
        fluentTranslator = FluentTranslator(QLocale(settings.language_code))
        self.installTranslator(fluentTranslator)
        self.installTranslator(settings.translator)
        # Pet Object
        self.p = PetWidget(screens=screens)
        # Notification System
        self.note = DPNote()
        # Accessory System
        self.acc = DPAccessory()
        # System Panel
        self.conp = ControlMainWindow()
        # Dashboard
        self.board = DashboardMainWindow()
        # Signal Links
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        # Main Widget - others
        self.p.setup_notification.connect(self.note.setup_notification)
        self.p.reset_sounds.connect(self.note.reset_sounds)
        self.p.change_note.connect(self.note.change_pet)
        self.p.change_note.connect(self.conp.charCardInterface._finishStateTooltip)
        self.p.hptier_changed_main_note.connect(self.note.hpchange_note)
        self.p.fvlvl_changed_main_note.connect(self.note.fvchange_note)
        self.p.setup_acc.connect(self.acc.setup_accessory)
        self.p.move_sig.connect(self.acc.send_main_movement)
        self.p.close_all_accs.connect(self.acc.closeAll)
        # System Widgets - others
        self.conp.settingInterface.ontop_changed.connect(self.acc.ontop_changed)
        self.conp.settingInterface.scale_changed.connect(self.acc.reset_size_sig)
        self.conp.settingInterface.ontop_changed.connect(self.p.ontop_update)
        self.conp.settingInterface.scale_changed.connect(self.p.reset_size)
        self.conp.settingInterface.lang_changed.connect(self.p.lang_changed)
        self.conp.charCardInterface.change_pet.connect(self.p._change_pet)
        self.p.show_controlPanel.connect(self.conp.show_window)
        self.conp.gamesaveInterface.refresh_pet.connect(self.p.refresh_pet)
        # Dashboard - others
        self.p.show_dashboard.connect(self.board.show_window)
        self.note.noteToLog.connect(self.board.statusInterface._addNote)
        self.p.hp_updated.connect(self.board.statusInterface.StatusCard._updateHP)
        self.p.fv_updated.connect(self.board.statusInterface.StatusCard._updateFV)
        self.p.change_note.connect(self.board.statusInterface._changePet)
        self.p.change_note.connect(self.board.chatInterface._changePet)
        self.board.statusInterface.changeStatus.connect(self.p._change_status)
        self.p.stopAllThread.connect(self.board.statusInterface.stopBuffThread)
        self.acc.acc_withdrawed.connect(self.board.backpackInterface.acc_withdrawed)
        self.board.backpackInterface.use_item_inven.connect(self.p.use_item)
        self.board.backpackInterface.item_note.connect(self.p.register_notification)
        self.board.backpackInterface.item_drop.connect(self.p.item_drop_anim)
        self.p.fvlvl_changed_main_inve.connect(self.board.backpackInterface.fvchange)
        self.p.fvlvl_changed_main_inve.connect(self.board.shopInterface.fvchange)
        self.p.addItem_toInven.connect(self.board.backpackInterface.add_items)
        self.p.compensate_rewards.connect(
            self.board.backpackInterface.compensate_rewards
        )
        self.p.refresh_bag.connect(self.board.backpackInterface.refresh_bag)
        self.p.refresh_bag.connect(self.board.shopInterface.refresh_shop)
        self.p.addCoins.connect(self.board.backpackInterface.addCoins)
        # Tasks and Timer
        self.board.taskInterface.focusPanel.start_pomodoro.connect(self.p.run_tomato)
        self.board.taskInterface.focusPanel.cancel_pomodoro.connect(
            self.p.cancel_tomato
        )
        self.board.taskInterface.focusPanel.start_focus.connect(self.p.run_focus)
        self.board.taskInterface.focusPanel.cancel_focus.connect(self.p.cancel_focus)
        self.p.taskUI_Timer_update.connect(
            self.board.taskInterface.focusPanel.update_Timer
        )
        self.p.taskUI_task_end.connect(self.board.taskInterface.focusPanel.taskFinished)
        self.p.single_pomo_done.connect(
            self.board.taskInterface.focusPanel.single_pomo_done
        )

        self.board.chatInterface.chatBot.start_speaking.connect(
            self.p.start_speaking_animation
        )
        self.board.chatInterface.chatBot.finish_speaking.connect(
            self.p.finish_speaking_animation
        )


if __name__ == "__main__":
    if platform == "win32":
        basedir = ""
    else:
        basedir = os.path.dirname(__file__)
    # Avoid multiple process
    try:
        me = singleton.SingleInstance()
    except:
        sys.exit()
    # Create App
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = DyberPetApp(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    sys.exit(app.exec())
