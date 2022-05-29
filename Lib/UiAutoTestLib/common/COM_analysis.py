from date.Chapters_data import MyData
import re
import types
from Lib.UiAutoTestLib.common import COM_utilities
import importlib
from Lib.UiAutoTestLib.common.COM_path import path_BASE_DIR, path_LOG_DIR

class MyAnalysis():
    """解析用例"""
    function_regexp = re.compile(r"^\$\{(\w+)\(([\$\w =,]*)\)\}$")
    stepdata_list = []
    Runlist = []
    Case_info = {}
    index = 0
    Case_dir = {}
    Runlist_dir = {}
    popup_list=[]
    path=None
    # path = os.path.join(path_YAML_FILES, "yamlCase/casedatas.yml")
    Popuopath = os.path.join(path_YAML_FILES, "yamlGame/popup.yml")


    def __init__(self):
        self.file_name()
        self.yaml_data(self.path)
        self.getrunlist()
        self.yaml_data_popup(self.Popuopath)

    def file_name(self):
        """解析当前路径的目录"""
        path = os.path.join(path_YAML_FILES, "yamlCase")
        for root, dirs, files in os.walk(path):
            # print(root) #当前目录路径
            # print(dirs) #当前路径下所有子目录
            # print(files) #当前路径下所有非目录子文件
            filesName=files[0].split(".yml")[0]
            self.Case_info["casename"]=filesName
            self.path=os.path.join(path, files[0])

    # def is_functon(self, content):
    #     matched = self.function_regexp.match(content)
    #     return True if matched else False

    def parse_function(self, content):
        """解析字符串"""
        function_meta = {
            "args": [],
            "kwargs": {}
        }
        matched = self.function_regexp.match(content)
        function_meta["func_name"] = matched.group(1)

        args_str = matched.group(2).replace(" ", "")
        if args_str == "":
            return function_meta

        args_list = args_str.split(',')
        for arg in args_list:
            if '=' in arg:
                key, value = arg.split('=')
                function_meta["kwargs"][key] = value
            else:
                function_meta["args"].append(arg)

        return function_meta

    # def is_function(self, tup):
    #     """ Takes (name, object) tuple, returns True if it is a function.
    #     """
    #     name, item = tup
    #     if isinstance(item, types.FunctionType):
    #         aa = eval(str(item.__name__))
    #     return

    # def import_module_functions(self, modules):
    #     """ import modules and bind all functions within the context
    #     """
    #     for module_name in modules:
    #         imported = importlib.import_module(module_name)
    #         imported_functions_dict = dict(filter(self.is_function, vars(imported).items()))
    #     return imported_functions_dict

    def yaml_data(self, path):
        """解析yamlcase数据"""
        function_meta = {
            "func_name": None,
            "args": [],
            "kwargs": {}
        }
        yamldata_dir = COM_utilities.read_yaml(path)
        for i, val in yamldata_dir.items():
            dir = {}
            dir.update({"casename": val["casename"]})
            dir.update({"casedec": val["casedec"]})
            dir.update({"reportname": val["reportname"]})
            dir.update({"caseauthor": val["caseauthor"]})
            dir.update({"repeattime": int(val["repeattime"])})
            self.Case_info[i] = dir
            caselist = yamldata_dir[i]["step"]
            for k in range(0, len(caselist)):
                function_meta = self.parse_function(caselist[k])
                function_meta["func_name"] = function_meta['func_name']
                function_meta["args"] = function_meta['args']
                function_meta["kwargs"] = function_meta['kwargs']
                self.stepdata_list.append(function_meta)
            self.Case_dir[i] = self.stepdata_list
            self.stepdata_list = []
    def yaml_data_popup(self, Popuopath):
        """解析yamlcase数据"""
        function_meta = {
            "popup_name": None,
            "element": [],
            "kwargs": {}
        }
        yamldatalist = COM_utilities.read_yaml(Popuopath)
        for i in range(0, len(yamldatalist)):
            self.index = i
            caselist = yamldatalist[i][i]["step"]
            for k in range(0, len(caselist)):
                thefunction_meta = self.parse_function(caselist[k])
                function_meta["Popupname"] = thefunction_meta['func_name']
                function_meta["element"] = thefunction_meta['args']
                function_meta["kwargs"] = thefunction_meta['kwargs']
                self.popup_list.append(thefunction_meta)
            MyData.popup_dir[i] = self.popup_list
            self.popup_list = []

    def getrunlist(self):
        for k, var in self.Case_dir.items():
            for i in range(0, len(var)):
                args = var[i]["args"]
                func_name = var[i]["func_name"]
                item = {"args": args, "func_name": func_name}
                self.Runlist.append(item)
            self.Runlist_dir[k] = self.Runlist
            self.Runlist = []

# MyAnalysis1=MyAnalysis()
# MyAnalysis1.yaml_data()