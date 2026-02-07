#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面宠物时钟 - Desktop Pet Clock
功能：
1. 系统托盘图标（右下角）
2. 桌面透明时钟
3. 可爱小宠物在桌面玩耍
"""

import sys
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QSystemTrayIcon, 
                             QMenu, QAction, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen, QIcon, QPixmap, QPainterPath

class DesktopClock(QWidget):
    """桌面时钟窗口"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 无边框、透明、置顶、不在任务栏显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置大小和位置
        self.setFixedSize(300, 100)
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - 320, 50)
        
        # 时钟标签
        self.time_label = QLabel(self)
        self.time_label.setGeometry(0, 0, 300, 70)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ff6b9d, stop:0.5 #ffc3a0, stop:1 #ff6b9d);
                font-size: 48px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Microsoft YaHei';
            }
        """)
        
        # 日期标签
        self.date_label = QLabel(self)
        self.date_label.setGeometry(0, 65, 300, 30)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 195, 160, 200);
                font-size: 16px;
                font-family: 'Microsoft YaHei';
            }
        """)
        
        # 定时器更新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
        # 拖动相关
        self.drag_pos = None
        
    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.date_label.setText(f"{now.year}年{now.month}月{now.day}日 {weekdays[now.weekday()]}")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制半透明背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        painter.fillPath(path, QBrush(QColor(30, 20, 50, 180)))
        
        # 绘制边框
        pen = QPen(QColor(255, 107, 157, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 20, 20)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)


class DesktopPet(QWidget):
    """桌面宠物窗口"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.init_behavior()
        
    def initUI(self):
        # 无边框、透明、置顶
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置大小
        self.setFixedSize(80, 80)
        
        # 初始位置
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.move(screen.width() // 2, screen.height() - 150)
        
        # 宠物状态
        self.state = 'idle'  # idle, walk_left, walk_right, jump, sleep
        self.frame = 0
        self.direction = 1  # 1=右, -1=左
        self.eye_blink = False
        self.tail_angle = 0
        
        # 拖动
        self.drag_pos = None
        self.being_dragged = False
        
    def init_behavior(self):
        # 动画定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(100)
        
        # 行为定时器
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.random_behavior)
        self.behavior_timer.start(3000)
        
        # 移动定时器
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_pet)
        self.move_timer.start(50)
        
    def random_behavior(self):
        if self.being_dragged:
            return
            
        behaviors = ['idle', 'walk_left', 'walk_right', 'idle', 'idle', 'jump']
        self.state = random.choice(behaviors)
        
        if self.state == 'walk_left':
            self.direction = -1
        elif self.state == 'walk_right':
            self.direction = 1
            
    def move_pet(self):
        if self.being_dragged:
            return
            
        if self.state in ['walk_left', 'walk_right']:
            new_x = self.x() + (3 * self.direction)
            # 边界检测
            if new_x < 0:
                new_x = 0
                self.direction = 1
                self.state = 'walk_right'
            elif new_x > self.screen_width - 80:
                new_x = self.screen_width - 80
                self.direction = -1
                self.state = 'walk_left'
            self.move(new_x, self.y())
            
    def animate(self):
        self.frame = (self.frame + 1) % 10
        self.eye_blink = (self.frame == 5)
        self.tail_angle = math.sin(self.frame * 0.6) * 20
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据方向翻转
        if self.direction == -1:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
        
        # 绘制小猫咪
        self.draw_cat(painter)
        
    def draw_cat(self, painter):
        # 身体 - 圆润的椭圆
        body_color = QColor(255, 180, 200)  # 粉色小猫
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 140, 160), 2))
        
        # 身体
        painter.drawEllipse(15, 30, 50, 40)
        
        # 头
        painter.drawEllipse(5, 10, 45, 40)
        
        # 耳朵
        ear_color = QColor(255, 150, 180)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        painter.drawPolygon([QPoint(10, 15), QPoint(5, -5), QPoint(25, 10)])
        # 右耳
        painter.drawPolygon([QPoint(35, 15), QPoint(45, -5), QPoint(25, 10)])
        
        # 耳朵内部
        inner_ear = QColor(255, 200, 210)
        painter.setBrush(QBrush(inner_ear))
        painter.drawPolygon([QPoint(12, 12), QPoint(10, 2), QPoint(22, 10)])
        painter.drawPolygon([QPoint(33, 12), QPoint(40, 2), QPoint(23, 10)])
        
        # 眼睛
        if self.eye_blink:
            # 闭眼 - 弧线
            painter.setPen(QPen(QColor(80, 60, 80), 2))
            painter.drawArc(12, 22, 10, 8, 0, 180 * 16)
            painter.drawArc(30, 22, 10, 8, 0, 180 * 16)
        else:
            # 睁眼
            painter.setBrush(QBrush(QColor(80, 60, 80)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(14, 20, 10, 12)
            painter.drawEllipse(32, 20, 10, 12)
            # 眼睛高光
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(17, 22, 4, 4)
            painter.drawEllipse(35, 22, 4, 4)
        
        # 鼻子
        painter.setBrush(QBrush(QColor(255, 150, 170)))
        painter.drawEllipse(24, 32, 6, 5)
        
        # 嘴巴
        painter.setPen(QPen(QColor(200, 140, 160), 1.5))
        painter.drawArc(20, 34, 8, 8, 200 * 16, 140 * 16)
        painter.drawArc(27, 34, 8, 8, 200 * 16, 140 * 16)
        
        # 胡须
        painter.setPen(QPen(QColor(150, 120, 140), 1))
        # 左边
        painter.drawLine(5, 30, 18, 32)
        painter.drawLine(3, 35, 18, 35)
        painter.drawLine(5, 40, 18, 38)
        # 右边
        painter.drawLine(50, 30, 37, 32)
        painter.drawLine(52, 35, 37, 35)
        painter.drawLine(50, 40, 37, 38)
        
        # 腿
        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor(200, 140, 160), 2))
        # 前腿
        leg_offset = math.sin(self.frame * 0.8) * 3 if self.state in ['walk_left', 'walk_right'] else 0
        painter.drawEllipse(20, 60 + leg_offset, 12, 15)
        painter.drawEllipse(40, 60 - leg_offset, 12, 15)
        
        # 尾巴
        painter.save()
        painter.translate(60, 45)
        painter.rotate(self.tail_angle)
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(-5, -5, 12, 30)
        painter.restore()
        
        # 腮红
        painter.setBrush(QBrush(QColor(255, 150, 180, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 30, 8, 5)
        painter.drawEllipse(38, 30, 8, 5)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.being_dragged = True
            self.state = 'idle'
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            
    def mouseReleaseEvent(self, event):
        self.being_dragged = False
        self.drag_pos = None


class PetClockApp:
    """主应用"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 创建组件
        self.clock = DesktopClock()
        self.pet = DesktopPet()
        
        # 创建系统托盘
        self.create_tray()
        
        # 显示
        self.clock.show()
        self.pet.show()
        
    def create_tray(self):
        # 创建托盘图标
        self.tray = QSystemTrayIcon()
        
        # 创建图标 (粉色爱心)
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 107, 157)))
        painter.setPen(Qt.NoPen)
        # 画爱心
        path = QPainterPath()
        path.moveTo(16, 28)
        path.cubicTo(0, 18, 0, 5, 10, 5)
        path.cubicTo(14, 5, 16, 10, 16, 10)
        path.cubicTo(16, 10, 18, 5, 22, 5)
        path.cubicTo(32, 5, 32, 18, 16, 28)
        painter.drawPath(path)
        painter.end()
        
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setToolTip("💕 桌面宠物时钟")
        
        # 创建菜单
        menu = QMenu()
        
        show_clock = QAction("显示/隐藏时钟", menu)
        show_clock.triggered.connect(self.toggle_clock)
        menu.addAction(show_clock)
        
        show_pet = QAction("显示/隐藏宠物", menu)
        show_pet.triggered.connect(self.toggle_pet)
        menu.addAction(show_pet)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
        
    def toggle_clock(self):
        if self.clock.isVisible():
            self.clock.hide()
        else:
            self.clock.show()
            
    def toggle_pet(self):
        if self.pet.isVisible():
            self.pet.hide()
        else:
            self.pet.show()
            
    def quit_app(self):
        self.tray.hide()
        self.app.quit()
        
    def run(self):
        return self.app.exec_()


if __name__ == '__main__':
    app = PetClockApp()
    sys.exit(app.run())
