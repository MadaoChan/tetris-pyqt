#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tetrominoe import Tetrominoe
import random

# 砖块类
class Shape(object):

    # CoordsTable是指每种砖块在游戏画面上的占位
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),       # 没有形状的砖块，空砖块，实际上不会使用
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),      # S型砖
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),       # Z型砖
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),       # 长条形砖
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),       # T型砖
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),       # 方块砖
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),       # 反L型砖
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))        # L型砖
    )

    def __init__(self):
        # 初始化都是空白砖块
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        # 设置的枚举就是NoShape型
        self.setShape(Tetrominoe.NoShape)


    # 返回砖块的类型，Tetrominoe枚举
    def shape(self):
        '''returns shape'''
        return self.pieceShape


    # 设置砖块的类型，并从坐标table中选取对应的砖块数组
    def setShape(self, shape):
        '''sets a shape'''

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape


    # 随即设置一种砖块（从1～7之中，0不使用）
    def setRandomShape(self):
        '''chooses a random shape'''
        self.setShape(random.randint(1, 7))


    # 返回X坐标的值（index取值范围在[0,3]）
    def x(self, index):
        '''returns x coordinate'''
        return self.coords[index][0]


    # 返回Y坐标的值（index取值范围在[0,3]）
    def y(self, index):
        '''returns y coordinate'''
        return self.coords[index][1]


    # 设置X坐标的值
    # index [0, 3]
    # x [-1, 1]
    def setX(self, index, x):
        '''sets x coordinate'''
        self.coords[index][0] = x


    # 设置Y坐标的值
    # index [0, 3]
    # x [-1, 1]
    def setY(self, index, y):
        '''sets y coordinate'''
        self.coords[index][1] = y


    # 返回当前方块中最小X坐标值
    def minX(self):
        '''returns min x value'''
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])
        return m


    # 返回当前方块中最大X坐标值
    def maxX(self):
        '''returns max x value'''
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])
        return m


    # 返回当前方块中最小Y坐标值
    def minY(self):
        '''returns min y value'''
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])
        return m


    # 返回当前方块中最大Y坐标值
    def maxY(self):
        '''returns max y value'''
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])
        return m


    # 砖块左转
    # 返回：旋转后的shape对象
    def rotateLeft(self):
        '''rotates shape to the left'''
        # 首先如果砖块是方型就不用转了
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
        # 返回的结果类也是Shape，直接new一个返回？？
        result = Shape()
        result.pieceShape = self.pieceShape
        # 左转实质是把原本Y的值映射到X上，把原本X的值映射到-Y上
        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))
        return result


    # 砖块右转
    # 返回：旋转后的shape对象
    def rotateRight(self):
        '''rotates shape to the right'''
        # 一样，如果是方型砖就不用转了
        if self.pieceShape == Tetrominoe.SquareShape:
            return self
        # 也是new一个新的shape返回
        result = Shape()
        result.pieceShape = self.pieceShape
        # 右转实质是把原来-Y的值映射到X上，把原本X的值映射到Y上
        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))
        return result