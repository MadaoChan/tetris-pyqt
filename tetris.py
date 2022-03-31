#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
"""

from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from board import Board
import sys


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):    
        '''initiates application UI'''
        # 建立一个Board对象，把窗口居中
        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        # 连接Board对象的信号和状态栏
        self.statusbar = self.statusBar()        
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        # Board开始
        self.tboard.start()

        self.resize(180, 380)
        self.center()
        self.setWindowTitle('Tetris')        
        self.show()


    def center(self):
        '''centers the window on the screen'''

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, 
            (screen.height()-size.height())/2)


if __name__ == '__main__':

    app = QApplication([])
    tetris = Tetris()    
    sys.exit(app.exec_())