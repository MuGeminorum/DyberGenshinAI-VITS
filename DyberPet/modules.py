import sys
import time
import math
import random
import inspect
import types
from datetime import datetime, timedelta

from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers import interval, date

from PyQt5.QtCore import Qt, QTimer, QObject, QPoint
from PyQt5.QtGui import QImage, QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from typing import List

from DyberPet.utils import *
from DyberPet.conf import *

#from win32api import GetMonitorInfo, MonitorFromPoint


import DyberPet.settings as settings


class Animation_worker(QObject):
    sig_setimg_anim = pyqtSignal(name='sig_setimg_anim')
    sig_move_anim = pyqtSignal(float, float, name='sig_move_anim')
    sig_repaint_anim = pyqtSignal()

    def __init__(self, pet_conf, parent=None):
        """
        Animation Module
        Display user-defined animations randomly
        :param pet_conf: PetConfig class object in Main Widgets

        """
        super(Animation_worker, self).__init__(parent)
        self.pet_conf = pet_conf
        self.is_killed = False
        self.is_paused = False

    def run(self):
        """Run animation in a separate thread"""
        print('start running pet %s'%(self.pet_conf.petname))
        while not self.is_killed:
            self.random_act()

            while self.is_paused:
                time.sleep(0.2)
            if self.is_killed:
                break

            time.sleep(self.pet_conf.refresh)
    
    def kill(self):
        self.is_paused = False
        self.is_killed = True

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
    

    def random_act(self) -> None:
        """
        随机执行动作
        :return:
        """
        # 如果菜单已打开, 则关闭菜单
        #if self.menu.isEnabled():
        #    self.menu.close()

        #if self.is_run_act:
        #    return

        #self.is_run_act = True
        # 选取随机动作执行
        prob_num = random.uniform(0, 1)
        act_index = sum([int(prob_num > self.pet_conf.act_prob[i]) for i in range(len(self.pet_conf.act_prob))])
        acts = self.pet_conf.random_act[act_index] #random.choice(self.pet_conf.random_act)
        self._run_acts(acts)

    def _run_acts(self, acts: List[Act]) -> None:
        """
        执行动画, 将一个动作相关的图片循环展示
        :param acts: 一组关联动作
        :return:
        """
        for act in acts:
            self._run_act(act)
        #self.is_run_act = False

    def _run_act(self, act: Act) -> None:
        """
        加载图片执行移动
        :param act: 动作
        :return:
        """
        for i in range(act.act_num):

            while self.is_paused:
                time.sleep(0.2)
            if self.is_killed:
                break

            for img in act.images:

                while self.is_paused:
                    time.sleep(0.2)
                if self.is_killed:
                    break

                #global current_img, previous_img
                settings.previous_img = settings.current_img
                settings.current_img = img
                self.sig_setimg_anim.emit()
                time.sleep(act.frame_refresh) ######## sleep 和 move 是不是应该反过来？
                #if act.need_move:
                self._move(act) #self.pos(), act)
                #else:
                #    self._static_act(self.pos())
                self.sig_repaint_anim.emit()

    def _static_act(self, pos: QPoint) -> None:
        """
        静态动作判断位置 - 目前舍弃不用
        :param pos: 位置
        :return:
        """
        screen_geo = QDesktopWidget().screenGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
        border = self.pet_conf.size
        new_x = pos.x()
        new_y = pos.y()
        if pos.x() < border:
            new_x = screen_width - border
        elif pos.x() > screen_width - border:
            new_x = border
        if pos.y() < border:
            new_y = screen_height - border
        elif pos.y() > screen_height - border:
            new_y = border
        self.move(new_x, new_y)

    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        移动动作
        :param pos: 当前位置
        :param act: 动作
        :return
        """
        #print(act.direction, act.frame_move)
        plus_x = 0.
        plus_y = 0.
        direction = act.direction
        if direction is None:
            pass
        else:
            if direction == 'right':
                plus_x = act.frame_move

            if direction == 'left':
                plus_x = -act.frame_move

            if direction == 'up':
                plus_y = -act.frame_move

            if direction == 'down':
                plus_y = act.frame_move

        self.sig_move_anim.emit(plus_x, plus_y)






class Interaction_worker(QObject):

    sig_setimg_inter = pyqtSignal(name='sig_setimg_inter')
    sig_move_inter = pyqtSignal(float, float, name='sig_move_inter')
    #sig_repaint_inter = pyqtSignal()
    sig_act_finished = pyqtSignal()

    def __init__(self, pet_conf, parent=None):
        """
        Interaction Module
        Respond immediately to signals and run functions defined
        
        pet_conf: PetConfig class object in Main Widgets

        """
        super(Interaction_worker, self).__init__(parent)
        self.pet_conf = pet_conf
        self.is_killed = False
        self.is_paused = False
        self.interact = None
        self.act_name = None # everytime making act_name to None, don't forget to set settings.playid to 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(self.pet_conf.interact_speed)

    def run(self):
        #print('start_run')
        if self.interact is None:
            return
        elif self.interact not in dir(self):
            self.interact = None
        else:
            getattr(self,self.interact)(self.act_name)

    def start_interact(self, interact, act_name=None):
        self.interact = interact
        self.act_name = act_name
    
    def kill(self):
        self.is_paused = False
        self.is_killed = True
        self.timer.stop()
        # terminate thread

    def pause(self):
        self.is_paused = True
        self.timer.stop()

    def resume(self):
        self.is_paused = False

    def img_from_act(self, act):
        #global playid
        #global current_img, previous_img
        #global current_act, previous_act

        if settings.current_act != act:
            settings.previous_act = settings.current_act
            settings.current_act = act
            settings.playid = 0

        n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
        img_list_expand = [item for item in act.images for i in range(n_repeat)] * act.act_num
        img = img_list_expand[settings.playid]

        settings.playid += 1
        if settings.playid >= len(img_list_expand):
            settings.playid = 0
        #img = act.images[0]
        settings.previous_img = settings.current_img
        settings.current_img = img
        #print(previous_img)
        #print(current_img)

    def animat(self, act_name):

        #global playid, act_id
        #global current_img, previous_img

        acts_index = self.pet_conf.random_act_name.index(act_name)
        acts = self.pet_conf.random_act[acts_index]
        #print(settings.act_id, len(acts))
        if settings.act_id >= len(acts):
            settings.act_id = 0
            self.interact = None
            self.sig_act_finished.emit()
        else:
            act = acts[settings.act_id]
            n_repeat = math.ceil(act.frame_refresh / (self.pet_conf.interact_speed / 1000))
            n_repeat *= len(act.images) * act.act_num
            self.img_from_act(act)
            if settings.playid >= n_repeat-1:
                settings.act_id += 1

            if settings.previous_img != settings.current_img:
                self.sig_setimg_inter.emit()
                self._move(act)
        

    def mousedrag(self, act_name):
        #global dragging, onfloor, set_fall
        #global playid
        #global current_img, previous_img
        # Falling is OFF
        if not settings.set_fall:
            if settings.draging==1:
                acts = self.pet_conf.drag

                self.img_from_act(acts)
                if settings.previous_img != settings.current_img:
                    self.sig_setimg_inter.emit()
                
            else:
                self.act_name = None
                settings.playid = 0

        # Falling is ON
        elif settings.set_fall==1 and settings.onfloor==0:
            if settings.draging==1:
                acts = self.pet_conf.drag
                self.img_from_act(acts)
                if settings.previous_img != settings.current_img:
                    self.sig_setimg_inter.emit()

            elif settings.draging==0:
                acts = self.pet_conf.fall
                self.img_from_act(acts)

                #global fall_right
                if settings.fall_right:
                    previous_img = settings.current_img
                    settings.current_img = settings.current_img.mirrored(True, False)
                if settings.previous_img != settings.current_img:
                    self.sig_setimg_inter.emit()

                self.drop()

        else:
            self.act_name = None
            settings.playid = 0

        #self.sig_repaint_inter.emit()

                
            

        #elif set_fall==0 and onfloor==0:

    def drop(self):
        #掉落
        #print("Dropping")
        #global dragspeedx, dragspeedy

        ##print(dragspeedx)
        ##print(dragspeedy)
        #dropnext=pettop+info.gravity*dropa-info.gravity/2
        plus_y = settings.dragspeedy #+ self.pet_conf.dropspeed
        plus_x = settings.dragspeedx
        settings.dragspeedy = settings.dragspeedy + self.pet_conf.gravity

        self.sig_move_inter.emit(plus_x, plus_y)

    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        在 Thread 中发出移动Signal
        :param act: 动作
        :return
        """
        #print(act.direction, act.frame_move)
        plus_x = 0.
        plus_y = 0.
        direction = act.direction

        if direction is None:
            pass
        else:
            if direction == 'right':
                plus_x = act.frame_move

            if direction == 'left':
                plus_x = -act.frame_move

            if direction == 'up':
                plus_y = -act.frame_move

            if direction == 'down':
                plus_y = act.frame_move

        self.sig_move_inter.emit(plus_x, plus_y)





class Scheduler_worker(QObject):
    sig_settext_sche = pyqtSignal(str, name='sig_settext_sche')
    sig_setact_sche = pyqtSignal(str, name='sig_setact_sche')
    sig_setstat_sche = pyqtSignal(str, int, name='sig_setstat_sche')

    def __init__(self, pet_conf, parent=None):
        """
        Animation Module
        Display user-defined animations randomly
        :param pet_conf: PetConfig class object in Main Widgets

        """
        super(Scheduler_worker, self).__init__(parent)
        self.pet_conf = pet_conf
        self.is_killed = False
        self.is_paused = False
        #self.activated_times = 0
        self.new_task = False
        self.task_name = None
        self.n_tomato=None
        self.n_tomato_now=None
        self.time_wait=None
        self.time_torun=None


        self.scheduler = QtScheduler()
        #self.scheduler.add_job(self.change_hp, 'interval', minutes=self.pet_conf.hp_interval)
        self.scheduler.add_job(self.change_hp, interval.IntervalTrigger(minutes=self.pet_conf.hp_interval))
        #self.scheduler.add_job(self.change_em, 'interval', minutes=self.pet_conf.em_interval)
        self.scheduler.add_job(self.change_hp, interval.IntervalTrigger(minutes=self.pet_conf.em_interval))
        self.scheduler.start()


    def run(self):
        """Run Scheduler in a separate thread"""
        now_time = datetime.now().hour
        greet_text = self.greeting(now_time)
        self.sig_settext_sche.emit(greet_text)
        time.sleep(3)
        self.sig_settext_sche.emit('None')
        '''
        while not self.is_killed:
            if self.new_task:
                #self.add_task()
                
            else:
                pass

            while self.is_paused:
                time.sleep(1)

            if self.is_killed:
                break

            time.sleep(1)
        '''
        
    
    def kill(self):
        self.is_paused = False
        self.is_killed = True
        self.scheduler.shutdown()


    def pause(self):
        self.is_paused = True
        self.scheduler.pause()


    def resume(self):
        self.is_paused = False
        self.scheduler.resume()


    def greeting(self, time):
        if 10 >= time >= 0:
            return '早上好!'
        elif 12 >= time >= 11:
            return '中午好!'
        elif 17 >= time >= 13:
            return '下午好！'
        elif 24 >= time >= 18:
            return '晚上好!'
        else:
            return 'None'
    '''
    def send_task(self, task_name, n_tomato=None, time_wait=None, time_torun=None):
        self.new_task = True
        self.task_name = task_name
        self.time_torun = time_torun
        self.n_tomato=n_tomato
        self.time_wait=time_wait
        self.time_torun=time_torun
    '''

    def add_task(self, task_name, n_tomato=None, time_wait=None, time_torun=None):

        if task_name == 'tomato' and self.n_tomato_now is None:
            self.n_tomato_now = n_tomato
            time_plus = 0 #25

            # 1-start
            task_text = 'tomato_first'
            time_torun = datetime.now() + timedelta(seconds=1)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_task, date.DateTrigger(run_date=time_torun), args=[task_text])
            time_plus += 25
            #1-end
            if n_tomato == 1:
                task_text = 'tomato_last'
            else:
                task_text = 'tomato_end'
            time_torun = datetime.now() + timedelta(minutes=time_plus)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_task, date.DateTrigger(run_date=time_torun), args=[task_text])
            time_plus += 5

            # others start and end
            if n_tomato > 1:
                for i in range(1, n_tomato):
                    #start
                    task_text = 'tomato_start'
                    time_torun = datetime.now() + timedelta(minutes=time_plus)
                    #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
                    self.scheduler.add_job(self.run_task, date.DateTrigger(run_date=time_torun), args=[task_text])
                    time_plus += 25
                    #end
                    if i == (n_tomato-1):
                        task_text = 'tomato_last'
                    else:
                        task_text = 'tomato_end'
                    time_torun = datetime.now() + timedelta(minutes=time_plus)
                    #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
                    self.scheduler.add_job(self.run_task, date.DateTrigger(run_date=time_torun), args=[task_text])
                    time_plus += 5

        elif task_name == 'tomato' and self.n_tomato_now is not None:
            task_text = "tomato_exist"
            time_torun = datetime.now() + timedelta(seconds=1)
            #self.scheduler.add_job(self.run_task, run_date=time_torun, args=[task_text])
            self.scheduler.add_job(self.run_task, date.DateTrigger(run_date=time_torun), args=[task_text])



    def run_task(self, task_text):
        if task_text == 'tomato_start':
            text_toshow = '新的番茄时钟开始了哦！加油！'
            self.sig_settext_sche.emit(text_toshow)
            time.sleep(3)
            self.sig_settext_sche.emit('None')
        elif task_text == 'tomato_first':
            text_toshow = "%s个番茄时钟设定完毕！开始了哦！"%(int(self.n_tomato_now))
            self.sig_settext_sche.emit(text_toshow)
            time.sleep(3)
            self.sig_settext_sche.emit('None')
        elif task_text == 'tomato_end':
            text_toshow = '叮叮~ 番茄时间到啦！休息5分钟！'
            self.sig_settext_sche.emit(text_toshow)
            time.sleep(3)
            self.sig_settext_sche.emit('None')
        elif task_text == 'tomato_last':
            #self.scheduler_dict['tomato'].shutdown()
            #self.scheduler_dict['tomato']=None
            self.n_tomato_now=None
            text_toshow = '叮叮~ 番茄时间全部结束啦！'
            self.sig_settext_sche.emit(text_toshow)
            time.sleep(3)
            self.sig_settext_sche.emit('None')
        elif task_text == 'tomato_exist':
            text_toshow = "不行！还有番茄钟在进行哦~"
            self.sig_settext_sche.emit(text_toshow)
            time.sleep(3)
            self.sig_settext_sche.emit('None')
        else:
            text_toshow = '叮叮~ 你的任务 [%s] 到时间啦！'%(task_text)

    def change_hp(self):
        self.sig_setstat_sche.emit('hp', -1)

    def change_em(self):
        self.sig_setstat_sche.emit('em', -1)


    def checktask(self):
        if self.activated_times == 0:
            now_time = datetime.now().hour
            greet_text = self.greeting(now_time)
            self.sig_settext_sche.emit(greet_text)
        elif self.activated_times == 4:
            self.sig_settext_sche.emit('None')

        if self.activated_times % (15*60) == 0 and self.activated_times>=(15*60):
            self.sig_setstat_sche.emit('hp', -1)
            self.sig_setstat_sche.emit('em', -1)

        self.activated_times += 1














































