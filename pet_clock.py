#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海绵宝宝电子宠物 - 完整版
功能：喂食、洗澡、玩耍、成长系统、状态特效
"""

import sys
import os
import json
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QSystemTrayIcon, 
                             QMenu, QAction, QDesktopWidget, QProgressBar,
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import (QFont, QColor, QPainter, QBrush, QPen, QIcon, 
                         QPixmap, QPainterPath, QLinearGradient, QRadialGradient)

# 数据保存路径
SAVE_FILE = os.path.join(os.path.dirname(__file__), 'pet_data.json')

class PetData:
    """宠物数据管理"""
    def __init__(self):
        self.name = "海绵宝宝"
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.hunger = 100  # 饱腹感 0-100
        self.health = 100  # 健康值 0-100
        self.clean = 100   # 清洁度 0-100
        self.happiness = 100  # 快乐值 0-100
        self.total_play_time = 0
        self.birth_date = datetime.now().isoformat()
        self.load()
        
    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.__dict__.update(data)
            except:
                pass
                
    def save(self):
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)
            
    def add_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.2)
        self.save()
        
    def feed(self):
        if self.hunger < 100:
            self.hunger = min(100, self.hunger + 30)
            self.happiness = min(100, self.happiness + 10)
            self.add_exp(10)
            return True
        return False
        
    def wash(self):
        if self.clean < 100:
            self.clean = min(100, self.clean + 40)
            self.health = min(100, self.health + 10)
            self.add_exp(10)
            return True
        return False
        
    def play(self):
        if self.hunger > 20:
            self.happiness = min(100, self.happiness + 25)
            self.hunger = max(0, self.hunger - 10)
            self.add_exp(15)
            return True
        return False
        
    def pet(self):
        self.happiness = min(100, self.happiness + 15)
        self.add_exp(5)
        return True
        
    def tick(self):
        """每分钟调用，数值自然下降"""
        self.hunger = max(0, self.hunger - 1)
        self.clean = max(0, self.clean - 0.5)
        if self.clean < 30:
            self.health = max(0, self.health - 0.5)
        if self.hunger < 20:
            self.happiness = max(0, self.happiness - 1)
        self.save()
        
    def get_mood(self):
        """获取当前心情状态"""
        if self.hunger < 20:
            return 'hungry'
        if self.clean < 30:
            return 'dirty'
        if self.health < 30:
            return 'sick'
        if self.happiness > 80:
            return 'happy'
        if self.happiness < 30:
            return 'sad'
        return 'normal'


class StatusPanel(QWidget):
    """状态面板"""
    def __init__(self, pet_data):
        super().__init__()
        self.pet_data = pet_data
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 180)
        
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - 220, 160)
        
        self.drag_pos = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, QBrush(QColor(40, 45, 80, 230)))
        
        # 边框
        painter.setPen(QPen(QColor(255, 220, 100, 100), 2))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 15, 15)
        
        # 标题
        painter.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        painter.setPen(QColor(255, 230, 150))
        painter.drawText(QRect(0, 8, self.width(), 25), Qt.AlignCenter, 
                        f"🧽 {self.pet_data.name} Lv.{self.pet_data.level}")
        
        # 状态条
        y = 40
        bars = [
            ("🍔 饱腹", self.pet_data.hunger, QColor(255, 180, 100)),
            ("💖 健康", self.pet_data.health, QColor(255, 100, 150)),
            ("🛁 清洁", self.pet_data.clean, QColor(100, 200, 255)),
            ("😊 快乐", self.pet_data.happiness, QColor(255, 220, 100)),
        ]
        
        painter.setFont(QFont("Microsoft YaHei", 9))
        for label, value, color in bars:
            # 标签
            painter.setPen(QColor(200, 200, 220))
            painter.drawText(10, y + 12, label)
            
            # 进度条背景
            painter.setBrush(QBrush(QColor(60, 60, 80)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(70, y, 110, 16, 8, 8)
            
            # 进度条
            bar_width = int(106 * value / 100)
            if bar_width > 0:
                gradient = QLinearGradient(70, y, 70 + bar_width, y)
                gradient.setColorAt(0, color)
                gradient.setColorAt(1, color.lighter(120))
                painter.setBrush(QBrush(gradient))
                painter.drawRoundedRect(72, y + 2, bar_width, 12, 6, 6)
            
            # 数值
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(QRect(70, y, 110, 16), Qt.AlignCenter, f"{int(value)}")
            
            y += 28
            
        # 经验条
        painter.setPen(QColor(200, 200, 220))
        painter.drawText(10, y + 12, "⭐ 经验")
        
        painter.setBrush(QBrush(QColor(60, 60, 80)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(70, y, 110, 16, 8, 8)
        
        exp_ratio = self.pet_data.exp / self.pet_data.exp_to_next
        bar_width = int(106 * exp_ratio)
        if bar_width > 0:
            gradient = QLinearGradient(70, y, 70 + bar_width, y)
            gradient.setColorAt(0, QColor(150, 100, 255))
            gradient.setColorAt(1, QColor(200, 150, 255))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(72, y + 2, bar_width, 12, 6, 6)
            
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(70, y, 110, 16), Qt.AlignCenter, 
                        f"{self.pet_data.exp}/{self.pet_data.exp_to_next}")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)


class SpongeBobPet(QWidget):
    """海绵宝宝宠物 - 带完整交互"""
    
    action_done = pyqtSignal(str)  # 动作完成信号
    
    def __init__(self, pet_data):
        super().__init__()
        self.pet_data = pet_data
        self.initUI()
        self.init_behavior()
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(140, 160)
        
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.move(screen.width() // 2, screen.height() - 200)
        
        # 动画状态
        self.state = 'idle'
        self.frame = 0
        self.direction = 1
        self.jump_height = 0
        self.jump_velocity = 0
        self.is_jumping = False
        
        # 特效
        self.particles = []  # 粒子特效
        self.show_bubble = False
        self.show_hearts = False
        self.show_food = False
        self.show_question = False
        self.show_dirt = False
        self.show_water = False
        
        # 表情参数
        self.eye_scale = 1.0
        self.mouth_open = 0.3
        self.arm_angle = 0
        self.leg_offset = 0
        self.body_squash = 1.0
        
        self.drag_pos = None
        self.being_dragged = False
        
    def init_behavior(self):
        # 动画定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(50)
        
        # 行为定时器
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.random_behavior)
        self.behavior_timer.start(3000)
        
        # 移动定时器
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_pet)
        self.move_timer.start(30)
        
        # 数值下降定时器（每分钟）
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.pet_data.tick)
        self.tick_timer.start(60000)
        
        # 特效定时器
        self.effect_timer = QTimer(self)
        self.effect_timer.timeout.connect(self.update_effects)
        self.effect_timer.start(100)
        
    def random_behavior(self):
        if self.being_dragged or self.state in ['eating', 'washing', 'playing']:
            return
            
        mood = self.pet_data.get_mood()
        
        if mood == 'hungry':
            self.state = 'hungry'
            self.show_question = True
        elif mood == 'dirty':
            self.state = 'dirty'
            self.show_dirt = True
        elif mood == 'sad':
            self.state = 'sad'
        elif mood == 'happy':
            behaviors = ['idle', 'walk', 'jump', 'dance', 'happy']
            self.state = random.choice(behaviors)
        else:
            behaviors = ['idle', 'idle', 'walk', 'walk', 'idle']
            self.state = random.choice(behaviors)
            
        if self.state == 'walk':
            self.direction = random.choice([-1, 1])
        elif self.state == 'jump' and not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = -12
            
    def do_feed(self):
        """喂食动作"""
        if self.pet_data.feed():
            self.state = 'eating'
            self.show_food = True
            self.show_question = False
            QTimer.singleShot(2000, self.finish_action)
            return True
        return False
        
    def do_wash(self):
        """洗澡动作"""
        if self.pet_data.wash():
            self.state = 'washing'
            self.show_water = True
            self.show_dirt = False
            QTimer.singleShot(2000, self.finish_action)
            return True
        return False
        
    def do_play(self):
        """玩耍动作"""
        if self.pet_data.play():
            self.state = 'playing'
            self.show_hearts = True
            QTimer.singleShot(2000, self.finish_action)
            return True
        return False
        
    def do_pet(self):
        """抚摸"""
        self.pet_data.pet()
        self.state = 'happy'
        self.show_hearts = True
        QTimer.singleShot(1500, self.finish_action)
        
    def finish_action(self):
        """动作完成"""
        self.state = 'idle'
        self.show_food = False
        self.show_water = False
        self.show_hearts = False
        self.action_done.emit('done')
        
    def move_pet(self):
        if self.being_dragged:
            return
            
        # 跳跃物理
        if self.is_jumping:
            self.jump_velocity += 0.8
            self.jump_height += self.jump_velocity
            if self.jump_height >= 0:
                self.jump_height = 0
                self.is_jumping = False
                self.jump_velocity = 0
                self.body_squash = 0.8
                QTimer.singleShot(100, lambda: setattr(self, 'body_squash', 1.0))
                
        # 行走
        if self.state == 'walk' and not self.is_jumping:
            new_x = self.x() + (3 * self.direction)
            if new_x < 0:
                new_x = 0
                self.direction = 1
            elif new_x > self.screen_width - 140:
                new_x = self.screen_width - 140
                self.direction = -1
            self.move(new_x, self.y())
            
    def update_effects(self):
        """更新粒子特效"""
        # 添加新粒子
        if self.show_hearts:
            if random.random() < 0.3:
                self.particles.append({
                    'type': 'heart',
                    'x': random.randint(30, 110),
                    'y': 60,
                    'vy': -2,
                    'life': 30
                })
        if self.show_water:
            if random.random() < 0.5:
                self.particles.append({
                    'type': 'water',
                    'x': random.randint(20, 120),
                    'y': 0,
                    'vy': 3,
                    'life': 40
                })
        if self.show_food:
            if random.random() < 0.2 and len([p for p in self.particles if p['type'] == 'food']) < 3:
                self.particles.append({
                    'type': 'food',
                    'x': random.randint(50, 90),
                    'y': 40,
                    'vy': 1,
                    'life': 20
                })
                
        # 更新粒子
        for p in self.particles:
            p['y'] += p['vy']
            p['life'] -= 1
            
        # 移除死亡粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        
    def animate(self):
        self.frame = (self.frame + 1) % 60
        mood = self.pet_data.get_mood()
        
        # 根据状态更新动画
        if self.state == 'idle':
            self.eye_scale = 1.0 + 0.05 * math.sin(self.frame * 0.2)
            self.mouth_open = 0.3
            self.arm_angle = 5 * math.sin(self.frame * 0.1)
            self.leg_offset = 0
            
        elif self.state == 'walk':
            self.eye_scale = 1.0
            self.mouth_open = 0.4
            self.arm_angle = 20 * math.sin(self.frame * 0.4)
            self.leg_offset = 8 * math.sin(self.frame * 0.4)
            
        elif self.state == 'hungry':
            self.eye_scale = 0.8
            self.mouth_open = 0.2
            self.arm_angle = 0
            # 身体微微晃动
            self.body_squash = 1.0 + 0.02 * math.sin(self.frame * 0.3)
            
        elif self.state == 'dirty':
            self.eye_scale = 0.9
            self.mouth_open = 0.2
            self.arm_angle = -10
            
        elif self.state == 'sad':
            self.eye_scale = 0.7
            self.mouth_open = 0.1
            self.arm_angle = -15
            
        elif self.state == 'happy' or self.state == 'playing':
            self.eye_scale = 1.2
            self.mouth_open = 0.7
            self.arm_angle = 30 * math.sin(self.frame * 0.5)
            self.leg_offset = 5 * math.sin(self.frame * 0.5)
            
        elif self.state == 'eating':
            self.eye_scale = 1.1
            self.mouth_open = 0.3 + 0.4 * abs(math.sin(self.frame * 0.5))
            self.arm_angle = 40
            
        elif self.state == 'washing':
            self.eye_scale = 0.8  # 闭眼
            self.mouth_open = 0.5
            self.arm_angle = 20 * math.sin(self.frame * 0.3)
            self.body_squash = 1.0 + 0.05 * math.sin(self.frame * 0.4)
            
        elif self.state == 'dance':
            self.eye_scale = 1.1
            self.mouth_open = 0.6
            self.arm_angle = 50 * math.sin(self.frame * 0.4)
            self.leg_offset = 12 * math.sin(self.frame * 0.4)
            self.body_squash = 1.0 + 0.08 * math.sin(self.frame * 0.3)
            
        elif self.state == 'jump':
            self.eye_scale = 1.3
            self.mouth_open = 0.8
            self.arm_angle = -40
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 跳跃偏移
        painter.translate(0, self.jump_height)
        
        # 方向翻转
        if self.direction == -1:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
            
        # 绘制特效（背景层）
        self.draw_effects_bg(painter)
        
        # 绘制海绵宝宝
        self.draw_spongebob(painter)
        
        # 绘制特效（前景层）
        self.draw_effects_fg(painter)
        
    def draw_effects_bg(self, painter):
        """绘制背景特效"""
        # 脏污特效
        if self.show_dirt or self.pet_data.clean < 30:
            painter.setBrush(QBrush(QColor(100, 80, 60, 100)))
            painter.setPen(Qt.NoPen)
            for i in range(8):
                x = 30 + (i * 17) % 80
                y = 40 + (i * 23) % 60
                painter.drawEllipse(x, y, 8 + i % 5, 6 + i % 4)
                
    def draw_effects_fg(self, painter):
        """绘制前景特效"""
        # 问号（饿了）
        if self.show_question or self.pet_data.hunger < 20:
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            painter.setPen(QColor(255, 200, 100))
            bob_y = 10 + 5 * math.sin(self.frame * 0.2)
            painter.drawText(int(55), int(bob_y), "?")
            
        # 粒子
        for p in self.particles:
            if p['type'] == 'heart':
                painter.setFont(QFont("Arial", 14))
                painter.setPen(QColor(255, 100, 150, int(255 * p['life'] / 30)))
                painter.drawText(int(p['x']), int(p['y']), "❤")
            elif p['type'] == 'water':
                painter.setBrush(QBrush(QColor(100, 200, 255, int(200 * p['life'] / 40))))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(int(p['x']), int(p['y']), 6, 10)
            elif p['type'] == 'food':
                painter.setFont(QFont("Arial", 16))
                painter.drawText(int(p['x']), int(p['y']), "🍔")
                
    def draw_spongebob(self, painter):
        """绘制海绵宝宝"""
        cx, cy = 70, 80
        
        # 应用身体变形
        painter.save()
        painter.translate(cx, cy + 50)
        painter.scale(1.0, self.body_squash)
        painter.translate(-cx, -(cy + 50))
        
        # ===== 腿 =====
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        leg_l = self.leg_offset
        painter.drawRect(45, 115 + leg_l, 14, 28)
        painter.drawRect(81, 115 - leg_l, 14, 28)
        
        # 鞋子
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(20, 20, 20), 1))
        painter.drawEllipse(42, 138 + leg_l, 20, 14)
        painter.drawEllipse(78, 138 - leg_l, 20, 14)
        
        # 袜子
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(200, 50, 50), 2))
        painter.drawRect(45, 130 + leg_l, 14, 10)
        painter.drawRect(81, 130 - leg_l, 14, 10)
        
        # ===== 手臂 =====
        painter.save()
        painter.translate(30, 80)
        painter.rotate(-self.arm_angle)
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.drawRect(-6, 0, 12, 32)
        painter.restore()
        
        painter.save()
        painter.translate(110, 80)
        painter.rotate(self.arm_angle)
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.drawRect(-6, 0, 12, 32)
        painter.restore()
        
        # ===== 身体 =====
        body_gradient = QLinearGradient(35, 35, 105, 120)
        body_gradient.setColorAt(0, QColor(255, 245, 120))
        body_gradient.setColorAt(0.5, QColor(255, 230, 80))
        body_gradient.setColorAt(1, QColor(240, 210, 60))
        
        painter.setBrush(QBrush(body_gradient))
        painter.setPen(QPen(QColor(200, 180, 50), 2))
        
        body_path = QPainterPath()
        body_path.moveTo(33, 35)
        body_path.lineTo(107, 35)
        body_path.lineTo(110, 40)
        body_path.lineTo(110, 115)
        body_path.lineTo(107, 120)
        body_path.lineTo(33, 120)
        body_path.lineTo(30, 115)
        body_path.lineTo(30, 40)
        body_path.closeSubpath()
        painter.drawPath(body_path)
        
        # 海绵孔洞
        painter.setBrush(QBrush(QColor(220, 200, 50)))
        painter.setPen(Qt.NoPen)
        holes = [(40, 45), (60, 40), (85, 47), (45, 62), (72, 58), (92, 65),
                 (43, 82), (65, 78), (88, 85), (50, 100), (75, 96)]
        for hx, hy in holes:
            size = random.randint(5, 8)
            painter.drawEllipse(hx, hy, size, size)
        
        # ===== 裤子 =====
        pants_gradient = QLinearGradient(30, 95, 110, 120)
        pants_gradient.setColorAt(0, QColor(140, 90, 60))
        pants_gradient.setColorAt(1, QColor(100, 60, 40))
        painter.setBrush(QBrush(pants_gradient))
        painter.setPen(QPen(QColor(80, 50, 30), 2))
        painter.drawRect(30, 98, 80, 24)
        
        # 腰带
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawRect(30, 95, 80, 7)
        
        # ===== 衬衫领子 =====
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        collar_l = QPainterPath()
        collar_l.moveTo(48, 35)
        collar_l.lineTo(65, 35)
        collar_l.lineTo(56, 50)
        collar_l.closeSubpath()
        painter.drawPath(collar_l)
        collar_r = QPainterPath()
        collar_r.moveTo(75, 35)
        collar_r.lineTo(92, 35)
        collar_r.lineTo(83, 50)
        collar_r.closeSubpath()
        painter.drawPath(collar_r)
        
        # 领带
        painter.setBrush(QBrush(QColor(220, 50, 50)))
        painter.setPen(QPen(QColor(180, 30, 30), 1))
        tie = QPainterPath()
        tie.moveTo(64, 37)
        tie.lineTo(76, 37)
        tie.lineTo(78, 52)
        tie.lineTo(70, 65)
        tie.lineTo(62, 52)
        tie.closeSubpath()
        painter.drawPath(tie)
        
        # ===== 脸部 =====
        eye_size = int(20 * self.eye_scale)
        
        # 眼白
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawEllipse(45 - eye_size//2 + 10, 50 - eye_size//2 + 5, eye_size, eye_size + 5)
        painter.drawEllipse(75 - eye_size//2 + 10, 50 - eye_size//2 + 5, eye_size, eye_size + 5)
        
        # 虹膜
        iris_size = int(11 * self.eye_scale)
        painter.setBrush(QBrush(QColor(100, 180, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(48 - iris_size//2 + 10, 55 - iris_size//2 + 5, iris_size, iris_size)
        painter.drawEllipse(78 - iris_size//2 + 10, 55 - iris_size//2 + 5, iris_size, iris_size)
        
        # 瞳孔
        pupil_size = int(5 * self.eye_scale)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawEllipse(50 - pupil_size//2 + 10, 57 - pupil_size//2 + 5, pupil_size, pupil_size)
        painter.drawEllipse(80 - pupil_size//2 + 10, 57 - pupil_size//2 + 5, pupil_size, pupil_size)
        
        # 眼睛高光
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(52 + 10, 53 + 5, 4, 4)
        painter.drawEllipse(82 + 10, 53 + 5, 4, 4)
        
        # 睫毛
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        for i in range(3):
            angle = -30 + i * 30
            lx = 55 + 12 * math.cos(math.radians(angle - 90))
            ly = 52 + 12 * math.sin(math.radians(angle - 90))
            painter.drawLine(int(lx), int(ly), int(lx + 6 * math.cos(math.radians(angle - 90))), 
                           int(ly + 6 * math.sin(math.radians(angle - 90))))
            lx2 = 85 + 12 * math.cos(math.radians(angle - 90))
            painter.drawLine(int(lx2), int(ly), int(lx2 + 6 * math.cos(math.radians(angle - 90))), 
                           int(ly + 6 * math.sin(math.radians(angle - 90))))
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 230, 100)))
        painter.setPen(QPen(QColor(200, 180, 50), 1))
        painter.drawEllipse(65, 65, 12, 14)
        
        # 腮红
        painter.setBrush(QBrush(QColor(255, 180, 180, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(38, 72, 14, 8)
        painter.drawEllipse(88, 72, 14, 8)
        
        # 嘴巴
        mouth_h = int(14 * self.mouth_open)
        painter.setBrush(QBrush(QColor(150, 50, 50)))
        painter.setPen(QPen(QColor(100, 30, 30), 2))
        painter.drawEllipse(50, 80, 40, mouth_h + 10)
        
        # 牙齿
        if self.mouth_open > 0.25:
            painter.setBrush(QBrush(Qt.white))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            tooth_h = min(12, int(mouth_h * 0.9))
            painter.drawRect(60, 81, 10, tooth_h)
            painter.drawRect(71, 81, 10, tooth_h)
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawLine(70, 81, 70, 81 + tooth_h)
        
        # 雀斑
        painter.setBrush(QBrush(QColor(220, 180, 50)))
        painter.setPen(Qt.NoPen)
        freckles = [(40, 68), (44, 74), (38, 78), (96, 68), (100, 74), (94, 78)]
        for fx, fy in freckles:
            painter.drawEllipse(fx, fy, 4, 4)
            
        painter.restore()
        
    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 45, 80, 240);
                border: 2px solid rgba(255, 220, 100, 150);
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 8px 25px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 220, 100, 100);
            }
        """)
        
        feed_action = QAction(f"🍔 喂食 (饱腹: {int(self.pet_data.hunger)})", self)
        feed_action.triggered.connect(self.do_feed)
        menu.addAction(feed_action)
        
        wash_action = QAction(f"🛁 洗澡 (清洁: {int(self.pet_data.clean)})", self)
        wash_action.triggered.connect(self.do_wash)
        menu.addAction(wash_action)
        
        play_action = QAction(f"🎮 玩耍 (快乐: {int(self.pet_data.happiness)})", self)
        play_action.triggered.connect(self.do_play)
        menu.addAction(play_action)
        
        pet_action = QAction("💕 摸摸头", self)
        pet_action.triggered.connect(self.do_pet)
        menu.addAction(pet_action)
        
        menu.exec_(event.globalPos())
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.being_dragged = True
            self.state = 'happy'
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            
    def mouseReleaseEvent(self, event):
        self.being_dragged = False
        self.drag_pos = None
        
    def mouseDoubleClickEvent(self, event):
        if not self.is_jumping:
            self.state = 'jump'
            self.is_jumping = True
            self.jump_velocity = -12


class DesktopClock(QWidget):
    """桌面时钟"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.glow_phase = 0
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(280, 100)
        
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - 300, 30)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(50)
        
        self.drag_pos = None
        
    def update_display(self):
        self.glow_phase = (self.glow_phase + 0.05) % (2 * math.pi)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 发光效果
        glow = int(30 + 15 * math.sin(self.glow_phase))
        for i in range(3):
            painter.setPen(QPen(QColor(255, 220, 100, glow - i * 10), 3 - i))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(i * 2, i * 2, self.width() - i * 4, self.height() - i * 4, 20, 20)
        
        # 背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 45, 80, 230))
        gradient.setColorAt(1, QColor(20, 25, 50, 250))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 18, 18)
        painter.fillPath(path, gradient)
        
        # 时间
        now = datetime.now()
        
        font = QFont("Consolas", 38, QFont.Bold)
        painter.setFont(font)
        
        text_gradient = QLinearGradient(0, 10, 0, 55)
        text_gradient.setColorAt(0, QColor(255, 230, 150))
        text_gradient.setColorAt(1, QColor(255, 180, 80))
        
        painter.setPen(QPen(QBrush(text_gradient), 1))
        painter.drawText(QRect(0, 5, self.width(), 55), Qt.AlignCenter, now.strftime("%H:%M:%S"))
        
        # 日期
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        date_str = f"{now.month}月{now.day}日 {weekdays[now.weekday()]}"
        
        painter.setFont(QFont("Microsoft YaHei", 12))
        painter.setPen(QColor(180, 200, 255, 200))
        painter.drawText(QRect(0, 60, self.width(), 30), Qt.AlignCenter, date_str)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)


class PetClockApp:
    """主应用"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 创建数据
        self.pet_data = PetData()
        
        # 创建组件
        self.clock = DesktopClock()
        self.pet = SpongeBobPet(self.pet_data)
        self.status = StatusPanel(self.pet_data)
        
        # 连接信号
        self.pet.action_done.connect(self.on_action_done)
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.status.update)
        self.status_timer.start(1000)
        
        # 创建托盘
        self.create_tray()
        
        # 显示
        self.clock.show()
        self.pet.show()
        self.status.show()
        
    def on_action_done(self, msg):
        self.status.update()
        
    def create_tray(self):
        self.tray = QSystemTrayIcon()
        
        # 创建图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 黄色方块（海绵宝宝）
        painter.setBrush(QBrush(QColor(255, 230, 80)))
        painter.setPen(QPen(QColor(200, 180, 50), 2))
        painter.drawRect(4, 4, 24, 24)
        
        # 眼睛
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 10, 8, 8)
        painter.drawEllipse(18, 10, 8, 8)
        
        painter.setBrush(QBrush(QColor(100, 180, 255)))
        painter.drawEllipse(10, 12, 4, 4)
        painter.drawEllipse(20, 12, 4, 4)
        
        # 嘴巴
        painter.setBrush(QBrush(QColor(150, 50, 50)))
        painter.drawEllipse(10, 20, 12, 6)
        
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(13, 20, 3, 3)
        painter.drawRect(17, 20, 3, 3)
        
        painter.end()
        
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip(f"🧽 {self.pet_data.name} Lv.{self.pet_data.level}")
        
        # 菜单
        menu = QMenu()
        
        show_all = QAction("📺 显示全部", menu)
        show_all.triggered.connect(self.show_all)
        menu.addAction(show_all)
        
        hide_all = QAction("🙈 隐藏全部", menu)
        hide_all.triggered.connect(self.hide_all)
        menu.addAction(hide_all)
        
        menu.addSeparator()
        
        toggle_clock = QAction("⏰ 时钟", menu)
        toggle_clock.triggered.connect(lambda: self.clock.setVisible(not self.clock.isVisible()))
        menu.addAction(toggle_clock)
        
        toggle_pet = QAction("🧽 海绵宝宝", menu)
        toggle_pet.triggered.connect(lambda: self.pet.setVisible(not self.pet.isVisible()))
        menu.addAction(toggle_pet)
        
        toggle_status = QAction("📊 状态面板", menu)
        toggle_status.triggered.connect(lambda: self.status.setVisible(not self.status.isVisible()))
        menu.addAction(toggle_status)
        
        menu.addSeparator()
        
        # 快捷操作
        feed = QAction("🍔 喂食", menu)
        feed.triggered.connect(self.pet.do_feed)
        menu.addAction(feed)
        
        wash = QAction("🛁 洗澡", menu)
        wash.triggered.connect(self.pet.do_wash)
        menu.addAction(wash)
        
        play = QAction("🎮 玩耍", menu)
        play.triggered.connect(self.pet.do_play)
        menu.addAction(play)
        
        menu.addSeparator()
        
        # 开机自启
        self.autostart_action = QAction("🚀 开机自启", menu)
        self.autostart_action.setCheckable(True)
        try:
            self.autostart_action.setChecked(is_autostart_enabled())
        except:
            pass
        self.autostart_action.triggered.connect(self.toggle_autostart)
        menu.addAction(self.autostart_action)
        
        menu.addSeparator()
        
        quit_action = QAction("❌ 退出", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()
        
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.pet.isVisible():
                self.hide_all()
            else:
                self.show_all()
                
    def show_all(self):
        self.clock.show()
        self.pet.show()
        self.status.show()
        
    def hide_all(self):
        self.clock.hide()
        self.pet.hide()
        self.status.hide()
        
    def quit_app(self):
        self.pet_data.save()
        self.tray.hide()
        self.app.quit()
        
    def toggle_autostart(self):
        enabled = self.autostart_action.isChecked()
        try:
            set_autostart(enabled)
            status = "已开启" if enabled else "已关闭"
            self.tray.showMessage("🧽 海绵宝宝", f"开机自启{status}", QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.tray.showMessage("🧽 海绵宝宝", f"设置失败: {e}", QSystemTrayIcon.Warning, 2000)
            self.autostart_action.setChecked(not enabled)
    
    def run(self):
        return self.app.exec_()


if __name__ == '__main__':
    app = PetClockApp()
    sys.exit(app.run())


# ===== 开机自启功能 =====
import winreg
import sys

def is_autostart_enabled():
    """检查是否已设置开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "SpongeBobPet")
        winreg.CloseKey(key)
        return True
    except:
        return False

def set_autostart(enable=True):
    """设置/取消开机自启"""
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Run",
                        0, winreg.KEY_SET_VALUE)
    if enable:
        # 获取当前脚本路径
        app_path = sys.executable if getattr(sys, 'frozen', False) else f'pythonw "{os.path.abspath(__file__)}"'
        winreg.SetValueEx(key, "SpongeBobPet", 0, winreg.REG_SZ, app_path)
    else:
        try:
            winreg.DeleteValue(key, "SpongeBobPet")
        except:
            pass
    winreg.CloseKey(key)
    return enable
