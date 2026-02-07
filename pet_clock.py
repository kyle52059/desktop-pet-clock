#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面宠物时钟 - 海绵宝宝版
功能：
1. 系统托盘图标（右下角）
2. 桌面透明时钟（更好看的设计）
3. 海绵宝宝在桌面玩耍（多种动作）
"""

import sys
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QSystemTrayIcon, 
                             QMenu, QAction, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import (QFont, QColor, QPainter, QBrush, QPen, QIcon, 
                         QPixmap, QPainterPath, QLinearGradient, QRadialGradient)


class DesktopClock(QWidget):
    """桌面时钟窗口 - 更精美的设计"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.glow_phase = 0
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 120)
        
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - 340, 30)
        
        # 定时器
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
        
        # 动态发光背景
        glow_intensity = int(30 + 15 * math.sin(self.glow_phase))
        
        # 外发光
        for i in range(3):
            glow_color = QColor(255, 220, 100, glow_intensity - i * 10)
            painter.setPen(QPen(glow_color, 3 - i))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(i * 2, i * 2, self.width() - i * 4, self.height() - i * 4, 25, 25)
        
        # 主背景 - 渐变
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 45, 80, 230))
        gradient.setColorAt(0.5, QColor(30, 35, 60, 240))
        gradient.setColorAt(1, QColor(20, 25, 50, 250))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        painter.fillPath(path, gradient)
        
        # 玻璃高光效果
        highlight = QLinearGradient(0, 0, 0, 40)
        highlight.setColorAt(0, QColor(255, 255, 255, 40))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        highlight_path = QPainterPath()
        highlight_path.addRoundedRect(5, 5, self.width() - 10, 35, 15, 15)
        painter.fillPath(highlight_path, highlight)
        
        # 时间
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        # 时间文字 - 渐变色
        font = QFont("Consolas", 42, QFont.Bold)
        painter.setFont(font)
        
        # 文字阴影
        painter.setPen(QColor(0, 0, 0, 100))
        painter.drawText(QRect(2, 12, self.width(), 60), Qt.AlignCenter, time_str)
        
        # 文字渐变
        text_gradient = QLinearGradient(0, 15, 0, 65)
        text_gradient.setColorAt(0, QColor(255, 230, 150))
        text_gradient.setColorAt(0.5, QColor(255, 200, 100))
        text_gradient.setColorAt(1, QColor(255, 180, 80))
        
        painter.setPen(QPen(QBrush(text_gradient), 1))
        painter.drawText(QRect(0, 10, self.width(), 60), Qt.AlignCenter, time_str)
        
        # 日期
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        date_str = f"{now.year}年{now.month}月{now.day}日 {weekdays[now.weekday()]}"
        
        font2 = QFont("Microsoft YaHei", 13)
        painter.setFont(font2)
        painter.setPen(QColor(180, 200, 255, 200))
        painter.drawText(QRect(0, 75, self.width(), 30), Qt.AlignCenter, date_str)
        
        # 装饰小星星
        painter.setPen(Qt.NoPen)
        star_alpha = int(150 + 100 * math.sin(self.glow_phase * 2))
        painter.setBrush(QColor(255, 220, 100, star_alpha))
        painter.drawEllipse(20, 20, 6, 6)
        painter.drawEllipse(self.width() - 26, 20, 6, 6)
        painter.drawEllipse(20, self.height() - 26, 6, 6)
        painter.drawEllipse(self.width() - 26, self.height() - 26, 6, 6)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)


class SpongeBob(QWidget):
    """海绵宝宝桌面宠物"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.init_behavior()
        
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(120, 140)
        
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.move(screen.width() // 2, screen.height() - 180)
        
        # 状态
        self.state = 'idle'  # idle, walk, jump, wave, laugh, dance
        self.frame = 0
        self.direction = 1
        self.jump_height = 0
        self.jump_velocity = 0
        self.is_jumping = False
        
        # 表情
        self.eye_scale = 1.0
        self.mouth_open = 0.3
        self.arm_angle = 0
        self.leg_offset = 0
        
        self.drag_pos = None
        self.being_dragged = False
        
    def init_behavior(self):
        # 动画定时器 - 更流畅
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(50)
        
        # 行为定时器
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.random_behavior)
        self.behavior_timer.start(2500)
        
        # 移动定时器
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_pet)
        self.move_timer.start(30)
        
    def random_behavior(self):
        if self.being_dragged or self.is_jumping:
            return
        behaviors = ['idle', 'idle', 'walk', 'walk', 'jump', 'wave', 'laugh', 'dance']
        weights = [20, 20, 25, 25, 10, 15, 15, 10]
        self.state = random.choices(behaviors, weights)[0]
        
        if self.state == 'walk':
            self.direction = random.choice([-1, 1])
        elif self.state == 'jump':
            self.is_jumping = True
            self.jump_velocity = -15
            
    def move_pet(self):
        if self.being_dragged:
            return
            
        # 跳跃物理
        if self.is_jumping:
            self.jump_velocity += 1  # 重力
            self.jump_height += self.jump_velocity
            if self.jump_height >= 0:
                self.jump_height = 0
                self.is_jumping = False
                self.jump_velocity = 0
                
        # 行走
        if self.state == 'walk' and not self.is_jumping:
            new_x = self.x() + (4 * self.direction)
            if new_x < 0:
                new_x = 0
                self.direction = 1
            elif new_x > self.screen_width - 120:
                new_x = self.screen_width - 120
                self.direction = -1
            self.move(new_x, self.y())
            
    def animate(self):
        self.frame = (self.frame + 1) % 60
        
        # 根据状态更新动画参数
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
            
        elif self.state == 'jump':
            self.eye_scale = 1.3
            self.mouth_open = 0.8
            self.arm_angle = -30
            self.leg_offset = 5
            
        elif self.state == 'wave':
            self.eye_scale = 1.1
            self.mouth_open = 0.6
            self.arm_angle = 60 + 30 * math.sin(self.frame * 0.5)
            self.leg_offset = 0
            
        elif self.state == 'laugh':
            self.eye_scale = 0.7 + 0.3 * abs(math.sin(self.frame * 0.3))
            self.mouth_open = 0.5 + 0.4 * abs(math.sin(self.frame * 0.4))
            self.arm_angle = 10 * math.sin(self.frame * 0.5)
            self.leg_offset = 3 * math.sin(self.frame * 0.6)
            
        elif self.state == 'dance':
            self.eye_scale = 1.0
            self.mouth_open = 0.5
            self.arm_angle = 40 * math.sin(self.frame * 0.3)
            self.leg_offset = 10 * math.sin(self.frame * 0.3)
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 应用跳跃偏移
        painter.translate(0, self.jump_height)
        
        # 根据方向翻转
        if self.direction == -1:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
            
        self.draw_spongebob(painter)
        
    def draw_spongebob(self, painter):
        cx, cy = 60, 70  # 中心点
        
        # ===== 腿 =====
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        # 左腿
        leg_l = self.leg_offset
        painter.drawRect(35, 105 + leg_l, 12, 25)
        # 右腿
        painter.drawRect(73, 105 - leg_l, 12, 25)
        
        # 鞋子
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(20, 20, 20), 1))
        painter.drawEllipse(32, 125 + leg_l, 18, 12)
        painter.drawEllipse(70, 125 - leg_l, 18, 12)
        
        # 袜子
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(200, 50, 50), 2))
        painter.drawRect(35, 118 + leg_l, 12, 8)
        painter.drawRect(73, 118 - leg_l, 12, 8)
        
        # ===== 手臂 =====
        painter.save()
        # 左臂
        painter.translate(25, 70)
        painter.rotate(-self.arm_angle)
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.drawRect(-5, 0, 10, 30)
        painter.restore()
        
        painter.save()
        # 右臂
        painter.translate(95, 70)
        painter.rotate(self.arm_angle)
        painter.setBrush(QBrush(QColor(255, 240, 150)))
        painter.setPen(QPen(QColor(255, 230, 100), 2))
        painter.drawRect(-5, 0, 10, 30)
        painter.restore()
        
        # ===== 身体（海绵） =====
        # 身体主体 - 黄色海绵
        body_gradient = QLinearGradient(30, 30, 90, 110)
        body_gradient.setColorAt(0, QColor(255, 245, 120))
        body_gradient.setColorAt(0.5, QColor(255, 230, 80))
        body_gradient.setColorAt(1, QColor(240, 210, 60))
        
        painter.setBrush(QBrush(body_gradient))
        painter.setPen(QPen(QColor(200, 180, 50), 2))
        
        # 海绵形状（略微不规则的矩形）
        body_path = QPainterPath()
        body_path.moveTo(28, 30)
        body_path.lineTo(92, 30)
        body_path.lineTo(95, 35)
        body_path.lineTo(95, 105)
        body_path.lineTo(92, 110)
        body_path.lineTo(28, 110)
        body_path.lineTo(25, 105)
        body_path.lineTo(25, 35)
        body_path.closeSubpath()
        painter.drawPath(body_path)
        
        # 海绵孔洞
        painter.setBrush(QBrush(QColor(220, 200, 50)))
        painter.setPen(Qt.NoPen)
        holes = [(35, 40), (55, 35), (75, 42), (40, 55), (65, 52), (80, 58),
                 (38, 75), (58, 70), (78, 78), (45, 92), (68, 88)]
        for hx, hy in holes:
            size = random.randint(4, 7)
            painter.drawEllipse(hx, hy, size, size)
        
        # ===== 裤子 =====
        pants_gradient = QLinearGradient(25, 85, 95, 110)
        pants_gradient.setColorAt(0, QColor(140, 90, 60))
        pants_gradient.setColorAt(1, QColor(100, 60, 40))
        painter.setBrush(QBrush(pants_gradient))
        painter.setPen(QPen(QColor(80, 50, 30), 2))
        painter.drawRect(25, 88, 70, 22)
        
        # 腰带
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawRect(25, 85, 70, 6)
        
        # ===== 衬衫领子 =====
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        # 左领
        collar_path_l = QPainterPath()
        collar_path_l.moveTo(40, 30)
        collar_path_l.lineTo(55, 30)
        collar_path_l.lineTo(48, 42)
        collar_path_l.closeSubpath()
        painter.drawPath(collar_path_l)
        # 右领
        collar_path_r = QPainterPath()
        collar_path_r.moveTo(65, 30)
        collar_path_r.lineTo(80, 30)
        collar_path_r.lineTo(72, 42)
        collar_path_r.closeSubpath()
        painter.drawPath(collar_path_r)
        
        # 领带
        painter.setBrush(QBrush(QColor(220, 50, 50)))
        painter.setPen(QPen(QColor(180, 30, 30), 1))
        tie_path = QPainterPath()
        tie_path.moveTo(56, 32)
        tie_path.lineTo(64, 32)
        tie_path.lineTo(66, 45)
        tie_path.lineTo(60, 55)
        tie_path.lineTo(54, 45)
        tie_path.closeSubpath()
        painter.drawPath(tie_path)
        
        # ===== 脸部 =====
        # 眼睛
        eye_size = int(18 * self.eye_scale)
        
        # 眼白
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawEllipse(38 - eye_size//2 + 45//2, 45 - eye_size//2 + 18//2, eye_size, eye_size + 4)
        painter.drawEllipse(62 - eye_size//2 + 45//2, 45 - eye_size//2 + 18//2, eye_size, eye_size + 4)
        
        # 虹膜（蓝色）
        iris_size = int(10 * self.eye_scale)
        painter.setBrush(QBrush(QColor(100, 180, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(42 - iris_size//2 + 45//2, 50 - iris_size//2 + 18//2, iris_size, iris_size)
        painter.drawEllipse(66 - iris_size//2 + 45//2, 50 - iris_size//2 + 18//2, iris_size, iris_size)
        
        # 瞳孔
        pupil_size = int(5 * self.eye_scale)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawEllipse(44 - pupil_size//2 + 45//2, 52 - pupil_size//2 + 18//2, pupil_size, pupil_size)
        painter.drawEllipse(68 - pupil_size//2 + 45//2, 52 - pupil_size//2 + 18//2, pupil_size, pupil_size)
        
        # 眼睛高光
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(46 + 45//2, 48 + 18//2, 3, 3)
        painter.drawEllipse(70 + 45//2, 48 + 18//2, 3, 3)
        
        # 睫毛
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        for i in range(3):
            angle = -30 + i * 30
            lx = 45 + 45//2 + 10 * math.cos(math.radians(angle - 90))
            ly = 45 + 18//2 + 10 * math.sin(math.radians(angle - 90))
            painter.drawLine(int(lx), int(ly), int(lx + 5 * math.cos(math.radians(angle - 90))), 
                           int(ly + 5 * math.sin(math.radians(angle - 90))))
            lx2 = 69 + 45//2 + 10 * math.cos(math.radians(angle - 90))
            painter.drawLine(int(lx2), int(ly), int(lx2 + 5 * math.cos(math.radians(angle - 90))), 
                           int(ly + 5 * math.sin(math.radians(angle - 90))))
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 230, 100)))
        painter.setPen(QPen(QColor(200, 180, 50), 1))
        painter.drawEllipse(55, 58, 10, 12)
        
        # 脸颊（腮红）
        painter.setBrush(QBrush(QColor(255, 180, 180, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(32, 65, 12, 8)
        painter.drawEllipse(76, 65, 12, 8)
        
        # 嘴巴
        mouth_height = int(12 * self.mouth_open)
        painter.setBrush(QBrush(QColor(150, 50, 50)))
        painter.setPen(QPen(QColor(100, 30, 30), 2))
        painter.drawEllipse(42, 72, 36, mouth_height + 8)
        
        # 牙齿
        if self.mouth_open > 0.3:
            painter.setBrush(QBrush(Qt.white))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            # 两颗大门牙
            tooth_h = min(10, int(mouth_height * 0.8))
            painter.drawRect(52, 73, 8, tooth_h)
            painter.drawRect(61, 73, 8, tooth_h)
            # 牙缝
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawLine(60, 73, 60, 73 + tooth_h)
        
        # 雀斑
        painter.setBrush(QBrush(QColor(220, 180, 50)))
        painter.setPen(Qt.NoPen)
        freckles = [(35, 60), (38, 65), (33, 68), (82, 60), (85, 65), (80, 68)]
        for fx, fy in freckles:
            painter.drawEllipse(fx, fy, 3, 3)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.being_dragged = True
            self.state = 'wave'  # 被拖动时挥手
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            
    def mouseReleaseEvent(self, event):
        self.being_dragged = False
        self.drag_pos = None
        self.state = 'idle'
        
    def mouseDoubleClickEvent(self, event):
        # 双击让海绵宝宝跳跃
        if not self.is_jumping:
            self.state = 'jump'
            self.is_jumping = True
            self.jump_velocity = -15


class PetClockApp:
    """主应用"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.clock = DesktopClock()
        self.pet = SpongeBob()
        self.create_tray()
        
        self.clock.show()
        self.pet.show()
        
    def create_tray(self):
        self.tray = QSystemTrayIcon()
        
        # 创建海绵宝宝图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 黄色方块
        painter.setBrush(QBrush(QColor(255, 230, 80)))
        painter.setPen(QPen(QColor(200, 180, 50), 2))
        painter.drawRect(4, 4, 24, 24)
        
        # 眼睛
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 10, 8, 8)
        painter.drawEllipse(18, 10, 8, 8)
        
        # 瞳孔
        painter.setBrush(QBrush(QColor(100, 180, 255)))
        painter.drawEllipse(10, 12, 4, 4)
        painter.drawEllipse(20, 12, 4, 4)
        
        # 嘴巴
        painter.setBrush(QBrush(QColor(150, 50, 50)))
        painter.drawEllipse(10, 20, 12, 6)
        
        # 牙齿
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(13, 20, 3, 3)
        painter.drawRect(17, 20, 3, 3)
        
        painter.end()
        
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip("🧽 海绵宝宝桌面时钟")
        
        menu = QMenu()
        
        show_clock = QAction("显示/隐藏时钟 ⏰", menu)
        show_clock.triggered.connect(self.toggle_clock)
        menu.addAction(show_clock)
        
        show_pet = QAction("显示/隐藏海绵宝宝 🧽", menu)
        show_pet.triggered.connect(self.toggle_pet)
        menu.addAction(show_pet)
        
        menu.addSeparator()
        
        quit_action = QAction("退出 ❌", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
        
        # 双击托盘图标显示/隐藏
        self.tray.activated.connect(self.tray_activated)
        
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.pet.isVisible():
                self.pet.hide()
                self.clock.hide()
            else:
                self.pet.show()
                self.clock.show()
                
    def toggle_clock(self):
        self.clock.setVisible(not self.clock.isVisible())
            
    def toggle_pet(self):
        self.pet.setVisible(not self.pet.isVisible())
            
    def quit_app(self):
        self.tray.hide()
        self.app.quit()
        
    def run(self):
        return self.app.exec_()


if __name__ == '__main__':
    app = PetClockApp()
    sys.exit(app.run())
