import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow

# 开始学习如何使用PyQtGraph，创建一个简单的窗口并画出一条曲线

class MyWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        # 1. 创建主窗口时先设置标题和大小
        '''
QWidget是Qt框架中所有用户界面部件的基类，包括窗口、对话框、按钮、标签、文本框、图形视图等等，它提供了基本的用户界面功能，例如绘制、事件处理、布局等。
而QMainWindow是QWidget的子类，是Qt框架中的一个主窗口类，它提供了一个应用程序的主界面，可以包含 菜单栏 、工具栏、状态栏、中心窗口等各种窗口部件。
        '''
        self.setWindowTitle("我的第一个PyQtGraph窗口")
        self.resize(800, 600)

        # 2. 创建一个画板架子并设为中心部件
        """
        画板是一个封装好的类，绘图容器，专门用来绘制多图表的表格什么的，提供了很多方便的功能，例如坐标轴、网格、图例等，可以直接使用它来绘制各种类型的图表。
        """
        self.graph_widget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graph_widget)

        # 3. 用 addPlot 添加一个画板，是画板的内置方法，返回一个PlotItem对象，可以在上面绘制各种图形
        self.plot = self.graph_widget.addPlot(title="一条简单的曲线", 
                                               labels={'left': 'Y值', 'bottom': 'X值'})
        # 4. 显示网格
        self.plot.showGrid(x=True, y=True, alpha=0.5)

        # 5. 生成数据并画出曲线
        # 生成x和y数据，x是0到9的整数，y是x的平方，数据类型是列表对象
        x = list(range(10))
        y = [i**2 for i in x]
        self.plot.plot(x, y, pen='r', symbol='o', symbolBrush='b')  # 红色线，蓝色圆点

# 程序启动的固定写法
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 开启应用
    window = MyWindow()
    window.show()                # 显示窗口
    sys.exit(app.exec_())        # 进入事件循环，等待用户操作


    """
    一个典型的PyQt应用程序包含以下部分：

    QApplication对象：每个PyQt应用程序都需要有一个QApplication实例
    窗口和控件：用户界面组件
    事件循环：处理用户输入和系统事件的循环
    事件处理器：响应事件的函数或方法
    """