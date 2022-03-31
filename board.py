from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QFrame
from tetrominoe import Tetrominoe
from shape import Shape


# 游戏主要逻辑类
class Board(QFrame):
    # 注册信号，这个信号是发往状态栏的
    msg2Statusbar = pyqtSignal(str)

    # 棋盘宽度10，高度22
    BoardWidth = 10
    BoardHeight = 22
    
    # 砖块下落速度为300
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()


    def initBoard(self):     
        '''initiates board'''
        # 使用Timer创建一个游戏循环
        self.timer = QBasicTimer()
        # 当前砖块是否已经到底
        self.isWaitingAfterLine = False
        # 当前X和Y
        self.curX = 0
        self.curY = 0
        # 已经消去的行数（分数值）
        self.numLinesRemoved = 0
        # 版图
        self.board = []
        # 设置StrongFocus，一进入游戏就有焦点
        self.setFocusPolicy(Qt.StrongFocus)
        # 游戏开始和暂停变量
        self.isStarted = False
        self.isPaused = False
        # 清理棋盘
        self.clearBoard()


    # 获取在X，Y坐标的砖块形状
    def shapeAt(self, x, y):
        '''determines shape at the board position'''
        return self.board[(y * Board.BoardWidth) + x]


    # 设置在X，Y坐标的砖块
    def setShapeAt(self, x, y, shape):
        '''sets a shape at the board'''
        self.board[(y * Board.BoardWidth) + x] = shape


    # 返回一个格子的宽度
    def squareWidth(self):
        '''returns the width of one square'''
        return self.contentsRect().width() // Board.BoardWidth


    # 返回一个格子的高度
    def squareHeight(self):
        '''returns the height of one square'''
        return self.contentsRect().height() // Board.BoardHeight


    # 开始游戏
    def start(self):
        '''starts game'''
        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False

        # 清空分数和游戏画面
        self.numLinesRemoved = 0
        self.clearBoard()

        # 向状态栏发送分数
        self.msg2Statusbar.emit(str(self.numLinesRemoved))

        # 新建一个砖块
        self.newPiece()
        # timer开始即时
        self.timer.start(Board.Speed, self)


    # 暂停游戏
    def pause(self):
        '''pauses game'''
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            # 暂停timer，并向状态栏发送paused消息
            self.timer.stop()
            self.msg2Statusbar.emit("paused")
        else:
            # 开始timer，并向状态栏发送分数信息
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))
        self.update()


    # 在游戏画面上画砖
    def paintEvent(self, event):
        '''paints all shapes of the game'''
        painter = QPainter(self)
        rect = self.contentsRect()
        # 获取画面的Top
        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight()

        # 绘制已经落下的砖块
        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)
                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                        rect.left() + j * self.squareWidth(),
                        boardTop + i * self.squareHeight(), shape)

        # 绘制正在落下的砖块
        if self.curPiece.shape() != Tetrominoe.NoShape:
            # 因为每一个砖块都是用长度为4的(x,y)元组来绘制
            # 所以可以用i in range(4)来画出当前方块
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                    self.curPiece.shape())


    # 响应按键事件（重写keyPressEvent）
    def keyPressEvent(self, event):
        '''processes key press events'''
        # 若游戏已经暂停，或者当前砖块是无砖块
        # 则忽略点击事件
        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()
        # 按P暂停
        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        # 左键是左移
        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)
        # 右键是右移
        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)
        # 下键是右转方块
        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
        # 上键是左转方块
        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
        # 空格是瞬间落下下落
        elif key == Qt.Key_Space:
            self.dropDown()
        # D是加速下落一行
        elif key == Qt.Key_D:
            self.oneLineDown()
        else:
            super(Board, self).keyPressEvent(event)


    # 重写timerEvent
    def timerEvent(self, event):
        '''handles timer event'''
        # 需要使用event.timerId()来判断当前到点的是那一个timer
        if event.timerId() == self.timer.timerId():
            if self.isWaitingAfterLine:
                # 砖块落到的了，就重置isWatingAfterLine状态
                # 然后new一块新的砖块
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                # 砖块未到底，则下落一行
                self.oneLineDown()
        else:
            super(Board, self).timerEvent(event)


    # 重置游戏，清空游戏画面
    def clearBoard(self):
        '''clears shapes from the board'''
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)


    # 砖块瞬间落到底的方法
    def dropDown(self):
        '''drops down a shape'''
        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1

        self.pieceDropped()


    # 当前砖块下落一行
    def oneLineDown(self):
        '''goes one line down with a shape'''
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()


    # 消去行
    def pieceDropped(self):
        '''after dropping shape, remove full lines and create new shape'''
        for i in range(4):
            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        # 尝试消除一行
        self.removeFullLines()
        # 若到时间了，就new一个砖块
        # 这里的isWatingAfterLine应该是由timeEvent触发的
        # 可以理解为，砖块到底后，等一个周期再new砖块
        if not self.isWaitingAfterLine:
            self.newPiece()


    def removeFullLines(self):
        '''removes all full lines from the board'''

        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight):

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()


        for m in rowsToRemove:

            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:

            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()


    # new一个砖块（随机new）
    def newPiece(self):
        '''creates a new shape'''

        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")


    # 尝试移动砖块
    def tryMove(self, newPiece, newX, newY):
        '''tries to move a shape'''

        for i in range(4):
            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True


    # 绘制砖块
    def drawSquare(self, painter, x, y, shape):
        '''draws a square of a shape'''        

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2, 
            self.squareHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1, 
            y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)
