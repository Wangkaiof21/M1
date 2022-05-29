from msilib.schema import Environment
from time import sleep
import os
import yaml
from numpy.core.defchararray import capitalize

from Lib.UiAutoTestLib.common.COM_path import path_BASE_DIR, path_LOG_DIR
from Lib.CommonLib.BaseLib.log_message import LogMessage, LOG_ERROR, LOG_INFO, LOG_DEBUG
from date.Chapters_API import APiClass
import sqlite3

FILE_NAME = os.path.split(__file__)[-1]


# TODO:书架需要考虑新手手书架情况
class UserData(APiClass):
    _instance = None

    def __init__(self):
        # self.adbpath = os.path.join(path_BASE_DIR, MyData.UserPath_dir["adbpath"])
        self.storyoptions_dir = {}
        self.bookread_result = {}
        self.bookInfo_dir = {}  # 书籍信息
        self.DeviceData_dir = {}  # 设备信息配置表
        self.DeviceData_dir["poco"] = None
        self.DeviceData_dir["androidpoco"] = None
        self.DeviceData_dir["offset"] = None
        self.EnvData_dir = {}  # 环境配置表
        self.reportConf = {}  # 自动阅读配置表
        self.UserData_dir = {}  # 用户基本数据表
        self.UserData_dir["bookDetailInfo"] = {}
        self.UserData_dir["bookDetailInfo"]["BookID"] = None
        self.UserData_dir["当前语言"] = None
        self.UserPath_dir = {}  # 用户自定义路径
        self.Bookshelf__dir = {}  # readprogressList 书籍列表
        self.Story_cfg_chapter_dir = {}  # 章节总信息表
        self.Stroy_data_dir = {}  # 书籍和ID对应关系
        self.readprogressList_dir = {}  # {'chapterProgress': 10108001, 'chatProgress': 10006} 书籍进度表
        self.chat_type_dir = {}  # 对话类型配置表
        self.popup_dir = {}  # 弹框配置表
        self.Element_dir = {}
        self.newPoP_dir = []
        self.checklist = []
        self.type_check_dir = {}
        self.downloadbook_sign = {}
        self.RpcClient = None
        self.dialogueResult_dir = {}
        self.selectResult_dir = {}
        self.Story_select_dir = {}
        self.fashion_dir = {}
        self.book_list = {}
        self.getdata()

        LogMessage(module=FILE_NAME, level=LOG_INFO, msg=f"完成数据初始化")
        print("导入用户数据成功")

    def getdata(self):
        self.clear()
        self.UserData_dir["channel_id"] = self.get_set()
        self.yamldata_conf()
        self.yaml_stroy()
        self.yaml_chattype()
        self.yaml_mobileconf()
        self.yaml_language()
        self.yaml_bookinfo()
        # self.yaml_bookread_result()
        self.format_bookread_yml()
        self.yaml_bookinfo()
        # self.yaml_bookread_result()
        self.yaml_newpopup()
        self.yaml_type_check()
        self.r_yaml_dialogue_result()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def yamldata_conf(self):
        # 读取yamlconf数据
        data = None
        loginInfo = {}
        path = os.path.join(path_YAML_FILES, "conf.yml")
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f.read(), Loader=yaml.Loader)
        uuid = data["UserData"]["uuid"]
        device_platform = data["UserData"]["device_platform"]
        device_id = data["UserData"]["device_id"]
        self.UserData_dir["device_id"] = device_id
        self.UserData_dir["uuid"] = uuid
        loginInfo["loginGuide"] = data["UserData"]["loginGuide"]
        loginInfo["loginemail"] = data["UserData"]["loginemail"]
        loginInfo["loginpassword"] = data["UserData"]["loginpassword"]
        self.UserData_dir["loginInfo"] = loginInfo
        self.UserData_dir["usertype"] = data["UserData"]["usertype"]
        self.EnvData_dir["packagepath"] = os.path.join(path_resource, data["EnvData"]["APKpackage"])
        self.EnvData_dir["packageName"] = data["EnvData"]["packageName"]
        self.EnvData_dir["ADBdevice"] = data["EnvData"]["ADBdevice"]
        self.EnvData_dir["ADBip"] = data["EnvData"]["ADBip"]
        self.EnvData_dir["device"] = data["EnvData"]["device"]
        self.EnvData_dir["method"] = data["EnvData"]["method"]
        self.EnvData_dir["simulator"] = data["EnvData"]["simulator"]
        self.EnvData_dir["sleepLevel"] = data["EnvData"]["sleepLevel"]
        self.UserPath_dir["errorLogpath"] = data["PathData"]["errorLogpath"]
        self.UserPath_dir["adbpath"] = data["PathData"]["adbpath"]
        self.UserPath_dir["Desktoppath"] = data["PathData"]["Desktoppath"]
        self.reportConf["des"] = data["ReportConf"]["des"]
        self.reportConf["powerOff"] = data["ReportConf"]["powerOff"]
        self.reportConf["sendDing"] = data["ReportConf"]["sendDing"]
        self.reportConf["DingUrl"] = data["ReportConf"]["DingUrl"]
        self.reportConf["endpoint"] = data["ReportConf"]["endpoint"]
        self.reportConf["accesskey_id"] = data["ReportConf"]["accesskey_id"]
        self.reportConf["accesskey_secret"] = data["ReportConf"]["accesskey_secret"]
        self.reportConf["bucket_name"] = data["ReportConf"]["bucket_name"]
        self.reportConf["baseUploadPath"] = data["ReportConf"]["baseUploadPath"]
        self.reportConf["url"] = data["ReportConf"]["url"]

        # if not self.UserData_dir["uuid"]:
        #     uuid = self.registerApi5(channel_id, device_id, device_platform)["user"]["uuid"]
        #     self.UserData_dir["uuid"] = uuid

    def read_yaml(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            value = yaml.safe_load(file)
        return value

    def r_yaml_select_result(self):
        """读选项记录"""
        file_path = os.path.join(path_YAML_FILES, "select_result.yml")
        with open(file_path, encoding='utf-8') as file:
            self.selectResult_dir = yaml.safe_load(file)
        if self.dialogueResult_dir is None:
            self.dialogueResult_dir = {'00001001': 1}
        return self.selectResult_dir

    def w_yaml_select_result(self):
        """写选项记录"""
        file_path = os.path.join(path_YAML_FILES, "select_result.yml")
        with open(file_path, 'w+', encoding="utf-8") as f:
            yaml.dump(self.selectResult_dir, f, allow_unicode=True)

    def r_yaml_dialogue_result(self):
        """读书籍对白阅读记录"""
        file_path = os.path.join(path_YAML_FILES, "dialogue_result.yml")
        with open(file_path, encoding='utf-8') as file:
            self.dialogueResult_dir = yaml.safe_load(file)
        if self.dialogueResult_dir is None:
            self.dialogueResult_dir = {'00001001': [10001]}
        return self.dialogueResult_dir

    def w_yaml_dialogue_result(self):
        """写对白阅读记录"""
        file_path = os.path.join(path_YAML_FILES, "dialogue_result.yml")
        with open(file_path, 'w+', encoding="utf-8") as f:
            yaml.dump(self.dialogueResult_dir, f, allow_unicode=True)

    def yaml_type_check(self):
        type_checkpath = os.path.join(path_YAML_FILES, "yamlGame/type_check.yml")
        self.type_check_dir = self.read_yaml(type_checkpath)

    def yaml_case(self):
        bookdetailpaths = os.path.join(path_YAML_FILES, "yamlCase\\bookdetail.yml")
        bookdetailData = self.read_yaml(bookdetailpaths)
        self.Element_dir["bookdetailData"] = bookdetailData

    def yaml_stroy(self):
        storyoptionspath = os.path.join(path_YAML_FILES, "yamlGame/storyoptions.yml")
        self.storyoptions_dir = self.read_yaml(storyoptionspath)

    def yaml_chattype(self):
        chattype = os.path.join(path_YAML_FILES, "yamlGame/chat_type.yml")
        self.chat_type_dir = self.read_yaml(chattype)
        return self.chat_type_dir

    def yaml_mobileconf(self):
        mobileconfpath = os.path.join(path_YAML_FILES, "mobileconf.yml")
        self.mobileconf_dir = self.read_yaml(mobileconfpath)
        return self.mobileconf_dir

    def yaml_language(self):
        yamllanguagepath = os.path.join(path_YAML_FILES, "yamllanguage/language_basics.yml")
        self.language_dir = self.read_yaml(yamllanguagepath)
        return self.language_dir

    def yaml_newpopup(self):
        yamlnewpopup_path = os.path.join(path_YAML_FILES, "yamlGame/newpopup.yml")
        with open(yamlnewpopup_path, encoding='utf-8') as file:
            self.newPoP_dir = yaml.safe_load(file)
        return self.newPoP_dir

    def yaml_bookinfo(self):
        """书籍阅读记录yml"""
        yamlbook_listpath = os.path.join(Desktoppath, "bookread_result.yml")
        self.book_list = self.read_yaml(yamlbook_listpath)
        return self.book_list

    def format_bookread_yml(self):
        """格式化书籍阅读记录yml"""
        mydir = {}
        if type(self.book_list) == dict:
            return
        try:
            list1 = self.book_list.split("[new]")
            if list1:
                for i in range(0, len(list1) - 1):
                    if "-" in list1[i]:
                        chapter = list1[i][len(list1[i]) - 17:len(list1[i])]
                        mydir[chapter] = None
                    else:
                        chapter = list1[i][len(list1[i]) - 8:len(list1[i])]
                        mydir[chapter] = None
            yamlbook_listpath = os.path.join(Desktoppath, "bookread_result.yml")
            with open(yamlbook_listpath, 'w+', encoding="utf-8") as f:
                yaml.dump(mydir, f, allow_unicode=True)
        except:
            print("检测列表格式异常！")

    def yaml_bookread_result(self):
        """书籍阅读结果"""
        file_path = os.path.join(Desktoppath, "bookread_result.yml")
        with open(file_path, encoding='utf-8') as file:
            self.book_list = yaml.safe_load(file)
        return self.book_list

    def update_record_bookread(self, chapter, result):
        """更新已经阅读的书籍信息"""
        if self.UserData_dir["usertype"] == "bookread":
            file_path = os.path.join(Desktoppath, "bookread_result.yml")
        else:
            file_path = os.path.join(Desktoppath, "bookread_result.yml")
        if type(self.book_list) != dict:
            self.book_list = {}
        self.book_list[chapter] = result
        with open(file_path, 'w+', encoding="utf-8") as f:
            yaml.dump(self.book_list, f, allow_unicode=True)
        print("记录阅读结果", self.book_list)
        return self.book_list

    def read_test(self):
        """输出errorlog日志转化到log.txt中"""
        pull = self.adbpath + " pull " + MyData.UserPath_dir["errorLogpath"] + " " + self.errorLogpath
        connected = self.adbpath + " connect " + MyData.EnvData_dir["ADBdevice"]
        print(pull)
        print(connected)
        with open(self.errorLogpath, "w") as errorLog_file:
            pass
        try:
            print(os.system(self.adbpath + " devices"))
            sleep(3)
            print(os.system(connected))
            sleep(3)
            print(os.popen(pull))
            print("完成读取errorlog")
        except BaseException as e:
            print("输出errorlog日志转化到log.txt中失败", e)

    def getbookData(self, language="en-US"):
        """大厅书架信息"""
        for i in self.language_dir:
            if i == language:
                language = self.language_dir[i]["formatName"]
        bookData = self.summaryApi3(self.UserData_dir["uuid"], language)  # es-ES,en-US
        areaData = bookData["area_data"]
        discover_data = bookData["discover_data"]
        bannerData = bookData["banner_data"]
        story_ids = bannerData["story_ids"]
        self.Bookshelf__dir["banner_data"] = story_ids
        for i in areaData:
            for k, v in i.items():
                if v == "Weekly Update":
                    story_ids = i["story_ids"]
                    self.Bookshelf__dir[v] = story_ids
        for i in areaData:
            for k, v in i.items():
                if v == "Weekly Update":
                    story_ids = i["story_ids"]
                    self.Bookshelf__dir[v] = story_ids

    def getreadprogress(self, bookid):
        """获取用户阅读进度返回chapterProgress和chatProgress"""
        datalist = self.getCommonDataApi(self.UserData_dir["uuid"])  # 调用通用接口0.章节进度，1.对话进度
        try:
            readprogress = datalist["data"]["readprogress"]
        except:
            raise Exception("请检查存档是否使用新存档，目前仅支持新存档")
        return readprogress

    def getBookInfo(self, uuid, bookId, channel_id="AVG10005"):
        """获取书籍信息"""
        data = self.booklistInfoApi(uuid=uuid, bookId=bookId)
        self.bookInfo_dir = data["data"]
        return self.bookInfo_dir

    def getreadprogress_local(self, StdPocoAgent):
        """获取本地用户阅读进度返回chapterProgress和chatProgress["Item2"]["Item3"]"""
        time = 6
        readprogress = None
        while time > 0:
            time -= 1
            try:
                readprogress = StdPocoAgent.get_ReadProgress()
                if readprogress:
                    return readprogress
            except:
                print("拉本地读书进度失败")
                sleep(1)

    def clear(self):
        """清空之前的报告和文件"""
        fileNamelist = [path_LOG_DIR, path_REPORT_DIR, path_RES_DIR]
        for fileName in fileNamelist:
            filelist = os.listdir(fileName)
            for f in filelist:
                filepath = os.path.join(fileName, f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        path = os.path.join(path_LOG_MY, "logging.log")
        with open(path, 'w') as f1:
            f1.seek(0)
            f1.truncate()
        self.w_yaml_dialogue_result()
        self.w_yaml_select_result()
        self.w_yaml_fashion()
        LogMessage(module=FILE_NAME, level=LOG_INFO, msg="完成文件清空")
        print("完成文件清空")

    def download_bookresource(self, bookid):
        """拉取书籍资源"""
        if bookid not in self.downloadbook_sign:
            self.avgcontentApi(bookid)
            self.downloadbook_sign[bookid] = True
            print("下载书籍资源成功")
        else:
            print("书籍资源已经下载")

    def read_story_cfg_chapter(self, bookid, chapter_id):
        """读取当前章节信息txt"""
        bookpath = bookid + "\\data_s\\" + chapter_id + "_chat.txt"
        selectpath = bookid + "\\data_s\\" + chapter_id + "_select.txt"
        path = os.path.join(path_resource, bookpath)
        path1 = os.path.join(path_resource, selectpath)
        with open(path, "r", encoding='utf-8') as f:  # 设置文件对象
            data = f.read()  # 可以是随便对文件的操作
            # print(data)
        data = eval(data)
        self.Story_cfg_chapter_dir = data
        self.Story_cfg_chapter_dir["length"] = len(data)
        with open(path1, "r", encoding='utf-8') as f:  # 设置文件对象
            selectdata = f.read()  # 可以是随便对文件的操作
        self.Story_select_dir = eval(selectdata)
        # self.getselectlist()
        return self.Story_cfg_chapter_dir

    # def getselectlist(self):
    #     mylist = list(self.Story_select_dir.keys())
    #     for i in mylist:
    #         self.selectResult_dir[i] = 0

    def getLoginStatus(self):
        """获取用户登陆状态"""
        LoginStatus = self.LoginStatusApi(self.UserData_dir["uuid"], self.UserData_dir["device_id"])
        self.UserData_dir["LoginStatus"] = LoginStatus
        return LoginStatus

    def stroy_data(self):
        """存在书籍和ID对应关系"""
        path = os.path.join(path_resource, "story_data.json")
        data = None
        with open(path, "r", encoding='utf-8') as f:  # 设置文件对象
            data = f.read()
        data = eval(data)["data"]
        for i in data:
            for j in i:
                self.Stroy_data_dir[i["story_id"]] = i["title"]
        return self.Stroy_data_dir

    def getAllStoryInfo(self, story_id):
        """获取书籍信息"""
        data = self.getAllStoryInfoApi(self.UserData_dir["uuid"])
        list = data["data"]["list"]
        for i in list:
            if i["story_id"] == story_id:
                print(i["title"])

    def getUsercurrency(self):
        """	虚拟币类型currency"""
        self.UserData_dir["diamond"] = self.syncValueApi(self.UserData_dir["uuid"], value_type="diamond")["value"]
        self.UserData_dir["ticket"] = self.syncValueApi(self.UserData_dir["uuid"], value_type="ticket")["value"]
        # credit = self.memberInfoApi(self.UserData_dir["uuid"])["data"]["credit"]
        # self.UserData_dir["credit"] = credit
        # return self.UserData_dir

    def updateUsercurrency(self, value_type, number):
        """	修改虚拟币类型currency"""
        self.syncValueApi(self.UserData_dir["uuid"], value_type=value_type, valuechange=number)

    def getUsermemberinfo(self):
        """获取会员相关信息"""
        member_type = self.memberInfoApi(self.UserData_dir["uuid"])["data"]["member_type"]
        self.UserData_dir["member_type"] = member_type

    def getstoryoptions(self, stroyID, stroychapter):
        for k in self.storyoptions_dir.keys():
            if stroyID == k:
                try:
                    stroyoptionlist = self.storyoptions_dir[k][stroychapter]
                    # print("stroyoptionlist", stroyoptionlist)
                    return stroyoptionlist
                except:
                    # print("无特殊选项")
                    return None
            else:
                return None

    def getDefaultFashion(self, bookid, role_id):
        """获取角色默认fashion"""
        role_id = str(role_id)
        if role_id not in self.fashion_dir:
            date = self.storyrole(book_id=bookid, role_ids=role_id)
            if len(date) > 0:
                role_list = self.getfashion_list(date[len(date) - 1], role_id)
            else:
                raise Exception("资源获取失败请检查渠道等相关配置是否正确", self.channel_id)
            newrole_list = self.getUserStoryData_fashion(self.UserData_dir["uuid"], bookid, role_id)
            if len(newrole_list) > 0:
                newlist = role_list + newrole_list
                newlist = sorted(set(newlist), key=newlist.index)
                self.fashion_dir[role_id] = newlist
                role_list = newlist
            else:
                self.fashion_dir[role_id] = role_list
            self.w_yaml_fashion()
        else:
            role_list = self.fashion_dir[role_id]
        print("默认角色", role_list)
        return role_list

    def getDIYFashion(self, fashion_id):
        """获取DIY装扮"""
        fashion_list = []

        if fashion_id is not None and fashion_id != "0":
            if fashion_id not in self.fashion_dir:
                fashion_id = str(fashion_id)
                data = self.fashionShowApi(fashion_ids=fashion_id)
                if len(data) > 0:
                    fashion_list = self.getfashion_list(data[len(data) - 1], fashion_id)
                # else:
                #     return False
                #     raise Exception("资源获取失败请检查渠道等相关配置是否正确",self.channel_id)
                self.fashion_dir[fashion_id] = fashion_list
                self.w_yaml_fashion()
            else:
                fashion_list = self.fashion_dir[fashion_id]
        print("DIY装扮", fashion_list)
        return fashion_list

    def getfashion(self, bookid, role_id, fashion_id=None):
        """获取最终形象"""
        role_list = self.getDefaultFashion(bookid, role_id)
        if fashion_id:
            DIY_list = []
            DIY_list = self.getDIYFashion(fashion_id)
            if len(DIY_list) > 0:
                endlist = role_list + DIY_list
                endlist = sorted(set(endlist), key=endlist.index)
                return endlist
            return role_list
        else:
            return role_list

    def getfashion_list(self, data, fashion_id):
        """装扮列表"""
        list = ['body', 'cloth', 'hair', 'back1', 'back2', 'back3', 'back4', 'dec1', 'dec2', 'dec4', 'dec5', 'face1',
                'face2']
        fashion_list = []
        for i in list:
            if i in data.keys():
                if data[i]:
                    k = i.capitalize()
                    fashion_list.append(k)
        self.fashion_dir[fashion_id] = fashion_list
        return fashion_list

    def getUserStoryData_fashion(self, uuid, bookid, roleid):
        """获取角色存档信息"""
        roleid_list = []
        list = ['body', 'cloth', 'hair', 'back1', 'back2', 'back3', 'back4', 'dec1', 'dec2', 'dec4', 'dec5', 'face1',
                'face2']
        roleidData = {}
        try:
            roleidData = self.getUserStoryDataApi(uuid, bookid)
            roleidData = roleidData["fashion"][str(roleid)]
            print("roleidData", roleidData)

        except:
            roleidData = {}
        if roleidData:
            for i in list:
                if i in roleidData.keys():
                    if roleidData[i]:
                        k = i.capitalize()
                        roleid_list.append(k)
        print("存档fashion列表", roleid_list)
        return roleid_list

    def updateUserRoleFashion(self, bookid, roleid):
        """更新角色装扮"""
        print("更新角色装扮")
        newlist = []
        newrole_list = self.getUserStoryData_fashion(self.UserData_dir["uuid"], bookid, roleid)
        if len(newrole_list) > 0:
            fashion_list = self.getfashion(bookid, roleid, fashion_id=None)
            newlist = newrole_list + fashion_list
            newlist = sorted(set(newlist), key=newlist.index)
            self.fashion_dir[roleid] = newlist
            self.w_yaml_fashion()
            print("有更新：", self.fashion_dir[roleid])
        print("self.fashion_dir", self.fashion_dir)

    def r_yaml_fashion(self):
        """读角色fashion"""
        file_path = os.path.join(path_YAML_FILES, "yamlBookRead/rolefashion.yml")
        with open(file_path, encoding='utf-8') as file:
            self.fashion_dir = yaml.safe_load(file)
        if self.fashion_dir is None:
            self.fashion_dir = {'000000': ["Body"]}
        return self.fashion_dir

    def w_yaml_fashion(self):
        """写角色fashion"""
        file_path = os.path.join(path_YAML_FILES, "yamlBookRead/rolefashion.yml")
        with open(file_path, 'w+', encoding="utf-8") as f:
            yaml.dump(self.fashion_dir, f, allow_unicode=True)


MyData = UserData()
# bookid = "52259"
# uuid="47447"
# role_id = "100022998"
# fashion_ids1 = "1000068307"
# # fashion_ids1="1000050135"
# # # role_id2="1605108"
# date=MyData.getUserStoryData_fashion(uuid,bookid,role_id)
# # # # MyData.r_yaml_fashion()
# date = MyData.getfashion(bookid, role_id, fashion_ids1)
# print(date)
# APiClass1 = APiClass()
# # fashion_dir={}
# bookid="52059"
# # role_id="16051"
# fashion_ids1="160510110"
# aa=APiClass1.getUserStoryDataApi(uuid="47395",book_id="52059")
# print(aa["fashion"]["100017243"])
