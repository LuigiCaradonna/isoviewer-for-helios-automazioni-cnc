# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ISOViewerMainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGraphicsView, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1366, 768)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.fr_canvas_container = QFrame(self.centralwidget)
        self.fr_canvas_container.setObjectName(u"fr_canvas_container")
        self.fr_canvas_container.setFrameShape(QFrame.StyledPanel)
        self.fr_canvas_container.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.fr_canvas_container)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(self.fr_canvas_container)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(50, 0))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 3, 0)
        self.canvas = QGraphicsView(self.frame)
        self.canvas.setObjectName(u"canvas")
        self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.gridLayout_3.addWidget(self.canvas, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btn_browse_file = QPushButton(self.fr_canvas_container)
        self.btn_browse_file.setObjectName(u"btn_browse_file")
        self.btn_browse_file.setMinimumSize(QSize(91, 31))
        self.btn_browse_file.setMaximumSize(QSize(91, 31))

        self.horizontalLayout_2.addWidget(self.btn_browse_file)

        self.lbl_selected_file = QLabel(self.fr_canvas_container)
        self.lbl_selected_file.setObjectName(u"lbl_selected_file")

        self.horizontalLayout_2.addWidget(self.lbl_selected_file)

        self.btn_draw = QPushButton(self.fr_canvas_container)
        self.btn_draw.setObjectName(u"btn_draw")
        self.btn_draw.setMinimumSize(QSize(101, 31))
        self.btn_draw.setMaximumSize(QSize(101, 31))
        font = QFont()
        font.setPointSize(14)
        self.btn_draw.setFont(font)

        self.horizontalLayout_2.addWidget(self.btn_draw)

        self.btn_reset = QPushButton(self.fr_canvas_container)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setMinimumSize(QSize(101, 31))
        self.btn_reset.setMaximumSize(QSize(101, 31))
        self.btn_reset.setFont(font)

        self.horizontalLayout_2.addWidget(self.btn_reset)

        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(0, 1)

        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.horizontalLayout.addWidget(self.fr_canvas_container)

        self.fr_right_col_container = QFrame(self.centralwidget)
        self.fr_right_col_container.setObjectName(u"fr_right_col_container")
        self.fr_right_col_container.setMinimumSize(QSize(221, 0))
        self.fr_right_col_container.setMaximumSize(QSize(221, 16777215))
        self.fr_right_col_container.setFrameShape(QFrame.StyledPanel)
        self.fr_right_col_container.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.fr_right_col_container)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_size = QLabel(self.fr_right_col_container)
        self.lbl_size.setObjectName(u"lbl_size")
        self.lbl_size.setMinimumSize(QSize(0, 21))
        self.lbl_size.setMaximumSize(QSize(16777215, 21))
        font1 = QFont()
        font1.setFamilies([u"Courier New"])
        font1.setPointSize(12)
        self.lbl_size.setFont(font1)
        self.lbl_size.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.verticalLayout_3.addWidget(self.lbl_size)


        self.verticalLayout_5.addLayout(self.verticalLayout_3)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lbl_width = QLabel(self.fr_right_col_container)
        self.lbl_width.setObjectName(u"lbl_width")
        self.lbl_width.setMinimumSize(QSize(0, 21))
        self.lbl_width.setMaximumSize(QSize(16777215, 21))
        self.lbl_width.setFont(font1)
        self.lbl_width.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.lbl_width, 0, 0, 1, 1)

        self.lbl_height = QLabel(self.fr_right_col_container)
        self.lbl_height.setObjectName(u"lbl_height")
        self.lbl_height.setMinimumSize(QSize(0, 21))
        self.lbl_height.setMaximumSize(QSize(16777215, 21))
        self.lbl_height.setFont(font1)
        self.lbl_height.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.lbl_height, 0, 1, 1, 1)

        self.in_width = QLineEdit(self.fr_right_col_container)
        self.in_width.setObjectName(u"in_width")
        self.in_width.setMinimumSize(QSize(0, 31))
        self.in_width.setMaximumSize(QSize(16777215, 31))
        self.in_width.setFont(font)
        self.in_width.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.in_width, 1, 0, 1, 1)

        self.in_height = QLineEdit(self.fr_right_col_container)
        self.in_height.setObjectName(u"in_height")
        self.in_height.setMinimumSize(QSize(0, 31))
        self.in_height.setMaximumSize(QSize(16777215, 31))
        self.in_height.setFont(font)
        self.in_height.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.in_height, 1, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_4)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.lbl_tool_speed = QLabel(self.fr_right_col_container)
        self.lbl_tool_speed.setObjectName(u"lbl_tool_speed")
        self.lbl_tool_speed.setMinimumSize(QSize(0, 31))
        self.lbl_tool_speed.setMaximumSize(QSize(16777215, 21))
        self.lbl_tool_speed.setFont(font1)
        self.lbl_tool_speed.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.verticalLayout_4.addWidget(self.lbl_tool_speed)

        self.in_tool_speed = QLineEdit(self.fr_right_col_container)
        self.in_tool_speed.setObjectName(u"in_tool_speed")
        self.in_tool_speed.setMinimumSize(QSize(0, 31))
        self.in_tool_speed.setMaximumSize(QSize(16777215, 31))
        self.in_tool_speed.setFont(font)
        self.in_tool_speed.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.in_tool_speed)


        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lbl_x_max_2 = QLabel(self.fr_right_col_container)
        self.lbl_x_max_2.setObjectName(u"lbl_x_max_2")
        self.lbl_x_max_2.setMinimumSize(QSize(0, 21))
        self.lbl_x_max_2.setMaximumSize(QSize(16777215, 21))
        self.lbl_x_max_2.setFont(font1)
        self.lbl_x_max_2.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.gridLayout_5.addWidget(self.lbl_x_max_2, 0, 1, 1, 1)

        self.lbl_x_min_value = QLabel(self.fr_right_col_container)
        self.lbl_x_min_value.setObjectName(u"lbl_x_min_value")
        self.lbl_x_min_value.setMinimumSize(QSize(0, 21))
        self.lbl_x_min_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_x_min_value.setFont(font1)
        self.lbl_x_min_value.setMidLineWidth(1)
        self.lbl_x_min_value.setAlignment(Qt.AlignCenter)

        self.gridLayout_5.addWidget(self.lbl_x_min_value, 1, 0, 1, 1)

        self.lbl_y_max = QLabel(self.fr_right_col_container)
        self.lbl_y_max.setObjectName(u"lbl_y_max")
        self.lbl_y_max.setMinimumSize(QSize(0, 21))
        self.lbl_y_max.setMaximumSize(QSize(16777215, 21))
        self.lbl_y_max.setFont(font1)
        self.lbl_y_max.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.gridLayout_5.addWidget(self.lbl_y_max, 2, 1, 1, 1)

        self.lbl_x_max = QLabel(self.fr_right_col_container)
        self.lbl_x_max.setObjectName(u"lbl_x_max")
        self.lbl_x_max.setMinimumSize(QSize(0, 21))
        self.lbl_x_max.setMaximumSize(QSize(16777215, 21))
        self.lbl_x_max.setFont(font1)
        self.lbl_x_max.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.gridLayout_5.addWidget(self.lbl_x_max, 2, 0, 1, 1)

        self.lbl_mix_x = QLabel(self.fr_right_col_container)
        self.lbl_mix_x.setObjectName(u"lbl_mix_x")
        self.lbl_mix_x.setMinimumSize(QSize(0, 21))
        self.lbl_mix_x.setMaximumSize(QSize(16777215, 21))
        self.lbl_mix_x.setFont(font1)
        self.lbl_mix_x.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.gridLayout_5.addWidget(self.lbl_mix_x, 0, 0, 1, 1)

        self.lbl_y_min_value = QLabel(self.fr_right_col_container)
        self.lbl_y_min_value.setObjectName(u"lbl_y_min_value")
        self.lbl_y_min_value.setMinimumSize(QSize(0, 21))
        self.lbl_y_min_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_y_min_value.setFont(font1)
        self.lbl_y_min_value.setAlignment(Qt.AlignCenter)

        self.gridLayout_5.addWidget(self.lbl_y_min_value, 1, 1, 1, 1)

        self.lbl_x_max_value = QLabel(self.fr_right_col_container)
        self.lbl_x_max_value.setObjectName(u"lbl_x_max_value")
        self.lbl_x_max_value.setMinimumSize(QSize(0, 21))
        self.lbl_x_max_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_x_max_value.setFont(font1)
        self.lbl_x_max_value.setAlignment(Qt.AlignCenter)

        self.gridLayout_5.addWidget(self.lbl_x_max_value, 3, 0, 1, 1)

        self.lbl_y_max_value = QLabel(self.fr_right_col_container)
        self.lbl_y_max_value.setObjectName(u"lbl_y_max_value")
        self.lbl_y_max_value.setMinimumSize(QSize(0, 21))
        self.lbl_y_max_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_y_max_value.setFont(font1)
        self.lbl_y_max_value.setAlignment(Qt.AlignCenter)

        self.gridLayout_5.addWidget(self.lbl_y_max_value, 3, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_5)

        self.lbl_rectangle = QLabel(self.fr_right_col_container)
        self.lbl_rectangle.setObjectName(u"lbl_rectangle")
        self.lbl_rectangle.setMinimumSize(QSize(0, 31))
        self.lbl_rectangle.setMaximumSize(QSize(16777215, 31))
        self.lbl_rectangle.setFont(font1)
        self.lbl_rectangle.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.verticalLayout_5.addWidget(self.lbl_rectangle)

        self.lbl_rectangle_value = QLabel(self.fr_right_col_container)
        self.lbl_rectangle_value.setObjectName(u"lbl_rectangle_value")
        self.lbl_rectangle_value.setMinimumSize(QSize(0, 21))
        self.lbl_rectangle_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_rectangle_value.setFont(font1)
        self.lbl_rectangle_value.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.lbl_rectangle_value)

        self.lbl_working_time = QLabel(self.fr_right_col_container)
        self.lbl_working_time.setObjectName(u"lbl_working_time")
        self.lbl_working_time.setMinimumSize(QSize(0, 31))
        self.lbl_working_time.setMaximumSize(QSize(16777215, 31))
        self.lbl_working_time.setFont(font1)
        self.lbl_working_time.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.verticalLayout_5.addWidget(self.lbl_working_time)

        self.lbl_working_time_value = QLabel(self.fr_right_col_container)
        self.lbl_working_time_value.setObjectName(u"lbl_working_time_value")
        self.lbl_working_time_value.setMinimumSize(QSize(0, 21))
        self.lbl_working_time_value.setMaximumSize(QSize(16777215, 21))
        self.lbl_working_time_value.setFont(font1)
        self.lbl_working_time_value.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.lbl_working_time_value)

        self.lbl_mouse_pos = QLabel(self.fr_right_col_container)
        self.lbl_mouse_pos.setObjectName(u"lbl_mouse_pos")
        self.lbl_mouse_pos.setMinimumSize(QSize(0, 21))
        self.lbl_mouse_pos.setMaximumSize(QSize(16777215, 21))
        self.lbl_mouse_pos.setFont(font1)
        self.lbl_mouse_pos.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.lbl_mouse_pos)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lbl_mmx = QLabel(self.fr_right_col_container)
        self.lbl_mmx.setObjectName(u"lbl_mmx")
        self.lbl_mmx.setMinimumSize(QSize(30, 0))
        self.lbl_mmx.setMaximumSize(QSize(30, 16777215))
        font2 = QFont()
        font2.setFamilies([u"Courier New"])
        font2.setPointSize(11)
        self.lbl_mmx.setFont(font2)
        self.lbl_mmx.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.lbl_mmx)

        self.lbl_mouse_pos_x = QLabel(self.fr_right_col_container)
        self.lbl_mouse_pos_x.setObjectName(u"lbl_mouse_pos_x")
        self.lbl_mouse_pos_x.setMinimumSize(QSize(70, 21))
        self.lbl_mouse_pos_x.setMaximumSize(QSize(70, 21))
        self.lbl_mouse_pos_x.setFont(font1)
        self.lbl_mouse_pos_x.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.lbl_mouse_pos_x)

        self.lbl_mmy = QLabel(self.fr_right_col_container)
        self.lbl_mmy.setObjectName(u"lbl_mmy")
        self.lbl_mmy.setMinimumSize(QSize(30, 0))
        self.lbl_mmy.setMaximumSize(QSize(30, 16777215))
        self.lbl_mmy.setFont(font2)
        self.lbl_mmy.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.lbl_mmy)

        self.lbl_mouse_pos_y = QLabel(self.fr_right_col_container)
        self.lbl_mouse_pos_y.setObjectName(u"lbl_mouse_pos_y")
        self.lbl_mouse_pos_y.setMinimumSize(QSize(70, 21))
        self.lbl_mouse_pos_y.setMaximumSize(QSize(70, 21))
        self.lbl_mouse_pos_y.setFont(font1)
        self.lbl_mouse_pos_y.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.lbl_mouse_pos_y)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.fr_right_col_container)

        self.horizontalLayout.setStretch(0, 1)

        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1366, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ISO Viewer", None))
        self.btn_browse_file.setText(QCoreApplication.translate("MainWindow", u"Load ISO file", None))
        self.lbl_selected_file.setText("")
        self.btn_draw.setText(QCoreApplication.translate("MainWindow", u"Avvia", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.lbl_size.setText(QCoreApplication.translate("MainWindow", u"Dimensioni lastra", None))
        self.lbl_width.setText(QCoreApplication.translate("MainWindow", u"L (mm)", None))
        self.lbl_height.setText(QCoreApplication.translate("MainWindow", u"A (mm)", None))
        self.in_width.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.in_height.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lbl_tool_speed.setText(QCoreApplication.translate("MainWindow", u"Velocit\u00e0 utensile", None))
        self.in_tool_speed.setText(QCoreApplication.translate("MainWindow", u"1000", None))
        self.lbl_x_max_2.setText(QCoreApplication.translate("MainWindow", u"Y min", None))
        self.lbl_x_min_value.setText("")
        self.lbl_y_max.setText(QCoreApplication.translate("MainWindow", u"Y max", None))
        self.lbl_x_max.setText(QCoreApplication.translate("MainWindow", u"X max", None))
        self.lbl_mix_x.setText(QCoreApplication.translate("MainWindow", u"X min", None))
        self.lbl_y_min_value.setText("")
        self.lbl_x_max_value.setText("")
        self.lbl_y_max_value.setText("")
        self.lbl_rectangle.setText(QCoreApplication.translate("MainWindow", u"Dimensione rettangolo", None))
        self.lbl_rectangle_value.setText("")
        self.lbl_working_time.setText(QCoreApplication.translate("MainWindow", u"Tempo stimato", None))
        self.lbl_working_time_value.setText("")
        self.lbl_mouse_pos.setText(QCoreApplication.translate("MainWindow", u"Posizione mouse", None))
        self.lbl_mmx.setText(QCoreApplication.translate("MainWindow", u"mmX", None))
        self.lbl_mouse_pos_x.setText("")
        self.lbl_mmy.setText(QCoreApplication.translate("MainWindow", u"mmY", None))
        self.lbl_mouse_pos_y.setText("")
    # retranslateUi
