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
        # 对data_dict处理,获取对应的x/y轴表值
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
        # 判断x_data_list下元素是否相同 进而判断不同配置下key的一致性
        if len(self.__list_in_list_set(x_data_list)) > 1:
            LogMessage(level=LOG_ERROR, module='bargraph_draw', msg=f"input data_dict second key is err \n {data_dict}")
            return False

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
        # 画条形图 line_width : 线宽 ,line_style : 线条类型 , label : 图例 ,marker : 数据点类型
        x_list = list(range(len(l2_key_list)))  # 多少组条形图
        bar_cnt = len(label_list)  # 每组有多少个条形图
        for bar_id in range(bar_cnt):
            x_label_list = [0.4 * (bar_cnt * i + bar_cnt) + 0.2 * i for i in x_list]
            plt.bar(x_label_list, y_data_list[bar_id], width=0.4, label=label_list[bar_id])
            if point_mark is False:
                continue
            for x, y in zip(x_label_list, y_data_list[bar_id]):
                plt.text(x, y, y, ha='center', va='bottom', fontsize=8)
        xtick_list = [i - 0.2 * (bar_cnt - 1) for i in x_label_list]
        plt.xticks(xtick_list, l2_key_list)
        plt.legend(loc='best')
        if png_path:
            plt.savefig(png_path)
            plt.show()
        return fig

    def pdf_savefig(self, pdf_file, fig_list):
        """
        将指定的fig_list 保存到指定的pdf_file下
        :param pdf_file:
        :param fig_list:
        :return:
        """
        with PdfPages(pdf_file)as pdf:
            for fig in fig_list:
                pdf.savefig(fig)

    def __get_float_list(self, str_list):
        """
        将str_list转换为float_list
        :param str_list:
        :return:
        """
        f_list = []
        for str_i in str_list:
            f_list.append(float(str_i))
        return f_list

    def __list_in_list_set(self, listinlist):
        """
        嵌套列表去重
        :param listinlist: [[1,2],[2,3],[1,2]] => [[1,2],[2,3]]
        :return:
        """
        list_o = []
        for item in listinlist:
            if item not in list_o:
                list_o.append(item)
        return list_o

    def dict_sorted(self, dict_in, sort_model):
        """
        对字典按照key排序
        :param dict_in:输入字典
        :param sort_model: 排序模式
        'int' 将key装换成int类型排序
        'float' 将key装换成float类型排序
        :return:
        """
        key_t_list = [eval(sort_model)(key) for key in dict_in.keys()]
        key_t2_list = list(sorted(key_t_list))
        dict_out = {}
        for key in key_t2_list:
            dict_out[str(key)] = dict_in.get(str(key))
        return dict_out


class BenchmarkDraw(Excel, MatPlot):
    # 从数据库/Excel表中读取指定测试数据 并基于MatPlot绘制折线图 直方图 保存在pdf文件中 便于分析
    def __init__(self, excel_path, sht_name):
        Excel.__init__(self, excel_path)
        MatPlot.__init__(self)
        self.sht_name = sht_name

    def sht_val_dict_search(self, sht_name, major_dict={}, search_keys=[]):
        """
        获取指定的sheet下,按照major_dict为索引条件,获取所有命中major_dict的dict_list 而后将对应search_keys的值输出
        :param sht_name: 如'stream'
        :param major_dict: {"TestCaseName":"test_perf_stream_0010","Host_ip":"198.8.88.163","MemNode":"0"}
        :param search_keys:['PhysCpu','BestRate']
        :return:
        """
        # 将sht转换成dict 判断major_dict，search_keys对应在sht_dict_list中的key能查到
        sht_dict_list = self.records_get(sht_name)
        sht_dict_keys_set = set(sht_dict_list[0].keys())
        major_keys = major_dict.keys()
        if not set(major_keys).issuperset(sht_dict_keys_set) or not set(search_keys).issuperset(sht_dict_keys_set):
            LogMessage(level=LOG_ERROR, module='sht_val_dict_search',
                       msg=f"major_keys or search_keys is not in sht_dict_keys {major_dict} {search_keys}")
            return False, []
        # 以 major_dict 为搜索条件 遍历sht_dict_list 获取所有命中的dict_list 并按照search_keys顺序输出命中值
        search_dict_list = []
        for sht_dict in sht_dict_list:
            major_set = set(major_dict.items())
            sht_dict_set = set(sht_dict.items())
            if major_set.issubset(sht_dict_set):
                search_dict = {}
                for search_key in search_keys:
                    search_dict[search_key] = sht_dict.get(search_key, None)
                search_dict_list.append(search_dict)
        return True, search_dict_list

    def bench_line_graph(self, major_dict, comp_dict, search_keys, axis_dict, png_path=None):
        """
        获取指定的sheet下,按照major_dict为索引条件,获取所有命中major_dict的dict_list 而后将对应search_keys的值输出
        根据输出值返回折线图 返回fig 调用pdf_savefig 以将对应的fig载入对应的pdf文件中
        :param major_dict: {"TestCaseName":"test_perf_stream_0010","Host_ip":"198.8.88.163","MemNode":"0"}
        :param comp_dict:
        {"Host_ip":{"127.0.0.1":True,"172.5.51.134":False},
        "data_keys":{"127.0.0.1":KunPeng920,"172.5.51.134":YiTian710},
        }
        MemNode指定excel表上对应的第一行key
        key- '0'/'1'/'2'/'3'/'4' 指示可选值
        val- True/False/True/False/True 指示对应图体现的数值
        data_keys标注在图标上体现关系
        :param search_keys: ['PhysCpu','BestRate'] 搜索对应项 最终输出PhysCpu->BestRate对应关系
        :param axis_dict: {'title':'Stream_Test(Triad)','xlabel':'core_num','ylabel':'triad_rate'}
        :param png_path: 路径 可不填
        :return: 对应fig
        """
        comp_val_list = list(list(comp_dict.values())[0].keys())
        comp_key = list(comp_dict.keys())[0]
        if len(list(comp_dict.keys())) > 1:
            data_keys_dict = comp_dict.get(list(comp_dict.keys())[1])
        else:
            data_keys_dict = {comp: comp for comp in comp_val_list}
        data_dict = {}
        for comp in comp_val_list:
            major_dict_t = dict(major_dict, **{comp_key: str(comp)})
            ret, search_dict_list = self.sht_val_dict_search(self.sht_name, major_dict=major_dict_t,
                                                             search_keys=search_keys)
            if not ret:
                LogMessage(level=LOG_ERROR, module="bench_line_graph", msg=f"find dict fail !!!")
            val_dict = self.__dictlist_to_xydict(search_dict_list)
            data_dict['{}_{}'.format(comp_key, data_keys_dict.get(comp))] = val_dict
        return self.bargraph_draw(axis_dict, data_dict, True, png_path)

    def bench_bargraph_graph(self, major_dict, comp_dict, search_keys, axis_dict, png_path=None):
        """
        获取指定的sheet下,按照major_dict为索引条件,获取所有命中major_dict的dict_list 而后将对应search_keys的值输出
        根据输出值返回折线图 返回fig 调用pdf_savefig 以将对应的fig载入对应的pdf文件中
        :param major_dict: {"TestCaseName":"test_perf_stream_0010","Host_ip":"198.8.88.163","MemNode":"0"}
        :param comp_dict:
        {"Host_ip":{"127.0.0.1":True,"172.5.51.134":False},
        "data_keys":{"127.0.0.1":KunPeng920,"172.5.51.134":YiTian710},
        }
        MemNode指定excel表上对应的第一行key
        key- '0'/'1'/'2'/'3'/'4' 指示可选值
        val- True/False/True/False/True 指示对应图体现的数值
        data_keys标注在图标上体现关系
        :param search_keys: ['PhysCpu','BestRate'] 搜索对应项 最终输出PhysCpu->BestRate对应关系
        :param axis_dict: {'title':'Stream_Test(Triad)','xlabel':'core_num','ylabel':'triad_rate'}
        :param png_path: 路径 可不填
        :return: 对应fig
        """
        comp_val_list = list(list(comp_dict.values())[0].keys())

        comp_key = list(comp_dict.keys())[0]
        if len(list(comp_dict.keys())) > 1:
            data_keys_dict = comp_dict.get(list(comp_dict.keys())[1])
        else:
            data_keys_dict = {comp: comp for comp in comp_val_list}

        data_dict = {}
        for comp in comp_val_list:
            major_dict_t = dict(major_dict, **{comp_key: str(comp)})
            ret, search_dict_list = self.sht_val_dict_search(self.sht_name, major_dict=major_dict_t,
                                                             search_keys=search_keys)
            if not ret:
                LogMessage(level=LOG_ERROR, module="bench_bargraph_graph", msg=f"find dict fail !!!")
            val_dict = self.__dictlist_to_xydict(search_dict_list)
            data_dict['{}_{}'.format(comp_key, data_keys_dict.get(comp))] = val_dict
        return self.bargraph_draw(axis_dict, data_dict, True, png_path)

    def bench_liner_graph(self, major_dict, comp_dict, search_keys, axis_dict, png_path=None):
        """
        获取指定的sheet下,按照major_dict为索引条件,获取所有命中major_dict的dict_list 而后将对应search_keys的值输出
        根据输出值返回折线图 返回fig 调用pdf_savefig 以将对应的fig载入对应的pdf文件中
        :param major_dict: {"TestCaseName":"test_perf_stream_0010","Host_ip":"198.8.88.163","MemNode":"0"}
        :param comp_dict:
        {"Host_ip":{"127.0.0.1":True,"172.5.51.134":False},
        "data_keys":{"127.0.0.1":KunPeng920,"172.5.51.134":YiTian710},
        }
        MemNode指定excel表上对应的第一行key
        key- '0'/'1'/'2'/'3'/'4' 指示可选值
        val- True/False/True/False/True 指示对应图体现的数值
        data_keys标注在图标上体现关系
        :param search_keys: ['PhysCpu','BestRate'] 搜索对应项 最终输出PhysCpu->BestRate对应关系
        :param axis_dict: {'title':'Stream_Test(Triad)','xlabel':'core_num','ylabel':'triad_rate'}
        :param png_path: 路径 可不填
        :return: 对应fig
        """
        comp_val_list = list(list(comp_dict.values())[0].keys())
        comp_mark_list = list(list(comp_dict.values())[0].values())

        comp_key = list(comp_dict.keys())[0]

        if len(list(comp_dict.keys())) > 1:
            data_keys_dict = comp_dict.get(list(comp_dict.keys())[1])
        else:
            data_keys_dict = {comp: comp for comp in comp_val_list}

        data_dict = {}
        for comp in comp_val_list:
            major_dict_t = dict(major_dict, **{comp_key: str(comp)})
            ret, search_dict_list = self.sht_val_dict_search(self.sht_name, major_dict=major_dict_t,
                                                             search_keys=search_keys)
            if not ret:
                LogMessage(level=LOG_ERROR, module="bench_liner_graph", msg=f"find dict fail !!!")
            val_dict = self.__dictlist_to_xydict(search_dict_list)
            # 计算线性度
            val_dict_t = {}
            key_lst = list(val_dict.keys())
            val_lst = list(val_dict.values())
            for i in range(len(key_lst)):
                if i == 0:
                    val = 1
                else:
                    val = float(val_lst[i]) / float(val_lst[0])
                val_dict_t[key_lst[i]] = round(val, 2)
            data_dict['{}_{}'.format(comp_key, data_keys_dict.get(comp))] = val_dict
        return self.line_graph_draw(axis_dict, data_dict, comp_mark_list, png_path)

    def __dictlist_to_xydict(self, dict_list):
        """
        将查表获取的dict 转换成 xy dict
        :param dict_list:
        :return:
        """
        xydict = {}
        for dict_t in dict_list:
            val_dist = list(dict_t.values())
            xydict[val_dist[0]] = val_dist[1]
        return xydict

    def __phycpu2corenum(self, phycpu_str):
        obj = re.search(r'(\d+)-(\d+)', phycpu_str)
        core_num = int(obj.group(2)) - int(obj.group(1)) + 1
        return str(core_num)
