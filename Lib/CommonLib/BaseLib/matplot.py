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

    def line_graph_draw(self, axis_dict=None, data_dict=None, mark_list=[], png_path=None):
        """
        依据data_dict画一个图
        :param axis_dict:
        {'title':'stream_test','xlabel':'core_num','ylabel':'triad_rate'}
        :param data_dict: 多个折线图的x/y值 key为x轴 value为y轴
        {'test1':{'1':'2','1':'0.1,'3':'2','52':'5','542':'5',}
        'test2':{'5':'5','555':'4','4':'1','2':'3','6':'7',}
        }
        :param mark_list: 折线对应点数值是否呈现 维度未data_dict个数
        :param png_path:png保存路径
        :return:
        """
        if data_dict is None or axis_dict is None or len(data_dict) == 0:
            LogMessage(level=LOG_ERROR, module='line_graph_draw', msg="input data_dict is None or Null")
            return False
        # 对data_dict处理
        x_data_list = []
        y_data_list = []
        label_list = list(data_dict.keys())
        for label_val in label_list:
            l2_dict = data_dict.get(label_val, {})
            l2_key_list = list(l2_dict.keys())
            l2_value_list = list(l2_dict.values())
            l2_fval_list = self.__get_float_list(l2_value_list)
            x_data_list.append(l2_key_list)
            y_data_list.append(l2_fval_list)

        fig = plt.figure()
        # 设置黑体字
        plt.rcParams['font.family'] = 'SimHei'
        # 设置折线图标题 x_label,y_label 并设置右边/top边框不显示
        plt.title(axis_dict.get('title', ''), fontsize=20)
        plt.xlabel(axis_dict.get('xlabel', ''), fontsize=14)
        plt.ylabel(axis_dict.get('ylabel', ''), fontsize=14)
        ax = plt.gca()
        ax.spines['right'].set_color('None')
        ax.spines['top'].set_color('None')

        # 画折线图 line_width : 线宽 ,line_style : 线条类型 , label : 图例 ,marker : 数据点类型
        for i in range(len(label_list)):
            plt.plot(x_data_list[i], y_data_list, label=label_list[i], linewidth=self.line_width,
                     linestyle=self.line_width, marker=self.market)
            if mark_list[i] is False:
                continue
            for x, y in zip(x_data_list[i], y_data_list[i]):
                plt.text(x, y, y, ha='center', va='bottom', fontsize=14)
        plt.legend(loc='best')
        if png_path:
            plt.savefig(png_path)
            plt.show()
        return fig

    def bargraph_draw(self, axis_dict=None, data_dict=None, point_mark=True, png_path=None):
        """
        根据data_dict画出2组以上的条形对比图 原则上是从data_dict相同的key取值做对比
        :param axis_dict:
        :param data_dict:
        {"ARM":{"core->node0":13416,"core->node1":12836,"core->node2":13555,"core->node3":15410},
         "YiTian710":{"core->node0":19987,"core->node1":17326,"core->node2":15435,"core->node3":15770},
         "X86 8163":{"core->node0":12416,"core->node1":12226,"core->node2":13255,"core->node3":17710},
        }
        :param point_mark: 条状图上是否做呈值
        :param png_path: 保存路径
        :return:
        """
