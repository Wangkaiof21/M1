#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/3 13:06
# @Author  : v_bkaiwang
# @File    : matplot.py
# @Software: win10 Tensorflow1.13.1 python3.6.3
import re
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages
from .excel import Excel as Excel
from .log_message import LogMessage, LOG_ERROR


class MatPlot:
    def __init__(self):
        # 折线图的定义
        self.line_width = 2
        self.line_style = ":"
        self.market = "o"

    def line_graph_draw(self):
        pass
