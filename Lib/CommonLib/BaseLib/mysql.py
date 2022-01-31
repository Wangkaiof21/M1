#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/30 10:18
# @Author  : v_bkaiwang
# @File    : mysql.py
# @Software: win10 Tensorflow1.13.1 python3.6.3

import time
import pymysql

from Lib.ComminLib.CoreLib.msg_center import MsgCenter
from GlobalConfig.global_config import MySqlCfg as Cfg
from Lib.ComminLib.BaseLib.log_message import LogMessage, LOG_ERROR, LOG_INFO


class Mysql:
    mysql = {}

    def __init__(self):
        """
        初始化配置

        """
        self.user = "root"
        self.port = Cfg.GLB_PROT
        self.password = Cfg.GLB_PASSWORD
        self.host = Cfg.GLB_HOST
        self.dbname = Cfg.GLB_DBNAME
        self.charset = Cfg.GLB_CHARSET

    def connent(self, times=3, interval_time=3):
        """
        数据库连接
        :param times: 重连次数
        :param interval_time: 间隔时间/休眠时间
        :return:
        """

        _times = 1
        _connected = False
        while _times <= times:
            try:
                self.mysql = pymysql.connect(host=self.host,
                                             port=self.port,
                                             user=self.user,
                                             password=self.password,
                                             db=self.dbname,
                                             cursorcclass=pymysql.cursors.DictCursor,
                                             read_timeout=20000
                                             )
                _connected = True
            except Exception as e:
                LogMessage(level=LOG_ERROR, module="Mysql",
                           msg="Mysql connect failed[ERROR:{}], please check".format(e))
                _times += 1
                time.sleep(interval_time)

            if _connected:
                # 连接成功 不重连 推出
                break

        return _connected

    def permission(self, usr, usr_pw, times=3, interval_time=3):
        permission_user = ['user', 'test']
        for user in permission_user:
            if usr == user:
                _times = 1
                _connected = False
                while _times <= times:
                    try:
                        self.mysql = pymysql.connect(host=self.host,
                                                     port=self.port,
                                                     user='root',
                                                     password='123456',
                                                     db=self.dbname,
                                                     cursorcclass=pymysql.cursors.DictCursor,
                                                     )
                        _connected = True
                    except Exception as e:
                        LogMessage(level=LOG_ERROR, module="Mysql",
                                   msg="Mysql connect failed[ERROR:{}], please check".format(e))
                        _times += 1
                        time.sleep(interval_time)
                    if _connected:
                        # 连接成功 不重连 推出
                        break

                    # 权限赋予
                    ex_order = f"GRANT ALL PRIVILEGES ON *.* TO '{usr}'@'%' IDENTIFIED BY '{usr_pw}' WITH GRANT OPTION;"
                    db = self.mysql
                    cursor = db.cursor()  # 建立游标
                    cursor.execute(ex_order)  # 执行赋予权限语句
                    cursor.execute("flush privileges;")  # 刷新权限

    def one_get(self, sql):
        """
        通过sql语句 返回一条对应记录
        :param sql: sql语句
        :return: 一条记录

        """
        # 大小写兼容处理 转换为小写
        sql = sql.lower()
        # 先判断连接状态
        if self.connent():
            db = self.mysql
            cursor = db.cursor()  # 建立游标
            result = ''  # 返回结果的初始值
            try:
                cursor.execute(sql)  # 执行sql
                result = cursor.fetchone()  # 返回一条数据
            except Exception as e:
                LogMessage(level=LOG_ERROR, module="Mysql", msg=e)
                db.rollback()
            cursor.close()
            self.close()
            return result

        else:
            return False

    def all_get(self, sql):
        """
        通过sql语句返回所有记录
        :param sql: 语句
        :return: 所有记录
        """
        # 大小写兼容处理 转换为小写
        sql = sql.lower()
        # 先判断连接状态
        if self.connent():
            db = self.mysql
            cursor = db.cursor()  # 建立游标
            result = ''  # 返回结果的初始值
            try:
                cursor.execute(sql)  # 执行sql
                result = cursor.fetchall()  # 返回一条数据
            except Exception as e:
                LogMessage(level=LOG_ERROR, module="Mysql", msg=e)
                db.rollback()
            cursor.close()
            self.close()
            return result

        else:
            return False

    def raw_sql(self, sql):
        """
        直接输入完整的sql进行查询
        :param sql: 原生sql
        :return: 所有查询记录
        """
        sql = sql.lower()
        print(sql)
        result = self.all_get(sql)
        LogMessage(level=LOG_ERROR, module="Mysql", msg=result)
        return result

    def execut(self, sql):
        """
        传入操作执行类sql 并执行
        :param sql: sql语句
        :return:
        """
        # 大小写兼容处理 转换为小写
        sql = sql.lower()
        # 先判断连接状态
        if self.connent():
            cursor = self.mysql.cursor()
            try:
                cursor.execute(sql)
                # 执行sql语句
                self.mysql.commit()
            except Exception as e:
                # 日志记录错误
                LogMessage(level=LOG_ERROR, module="Mysql", msg=e)
                # 发生错误时回滚
                self.mysql.rollback()
            # 关闭游标
            cursor.close()
            # 关闭链接
            self.mysql.close()
            return cursor
        else:
            return False

    def count_get(self, table, condition='', quiet=False):
        """
        传入表名及其条件 返回记录错误
        :param table: 表名
        :param condition: 精确条件
        :param quiet: 静默模式
        :return: 对应记录数量

        """
        # 大小写兼容处理 转换为小写 兼容处理
        table = table.lower()
        if condition:
            condition = "where {}".format(condition)
            # 大小写兼容处理 转换为小写 兼容处理
            condition = condition.lower()
        sql = "select count(*) from {} {}".format(table, condition).strip() + ";"
        result = self.one_get(sql)
        if not quiet:
            LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, result))
        return result

    def database_select(self, db_name, charset=""):
        """
        通过数据库名字，编码格式，进行切换数据库
        :param db_name: 数据库名字
        :param charset: 编码类型
        :return:  数据库对象

        """
        self.dbname = db_name
        if charset:
            self.charset = charset
        return self

    def database_create(self, db_name, charset=""):
        """
        通过数据库名字，编码格式，进行数据库创建
        :param db_name: 库名
        :param charset: 编码类型
        :return: 数据库对象
        """
        # 大小写兼容处理 转换为小写 兼容处理
        db_name = db_name.lower()
        # 命令状态标识
        cmd_status = True
        if not charset:
            sql = "create database {};".format(db_name)
        else:
            sql = "create database {} char set {};".format(db_name, charset)
        if self.database_exist(db_name):
            LogMessage(level=LOG_ERROR, module="Mysql", msg="Database[{}] has been exist".format(db_name))
            cmd_status = False
        else:
            if self.execut(sql):
                # 检查是否创建成功
                if not self.database_exist(db_name, quiet=True):
                    cmd_status = False
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status
    
    def database_show(self, quiet=False):
        """
        查询所有数据库
        
        :param quiet: 静默模式 默认关闭 
        :return: 所有数据库
        
        """
        sql = "show databases;"
        database_data = self.all_get(sql)
        if not quiet:
            LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, database_data))
        return database_data
    
    def database_exist(self, db_name, quiet=False):
        """
        通过库名查询数据库在不在
        :param db_name: 库名
        :param quiet: 静默模式 默认关闭 
        :return:  执行状态 True or False
        
        """
        cmd_status = True
        database_data = self.database_show(quiet=quiet)
        database_str = ",".join([value for database in database_data for key, value in database.items()])
        if db_name not in database_str:
            cmd_status = False
        return cmd_status

    def database_drop(self, db_name):
        """
        通过传入名 删除数据库
        :param db_name: 数据库名
        :return: 执行状态 True or False
        """
        # 大小写兼容处理
        db_name = db_name.lower()
        # 命令状态标识
        cmd_status = True
        sql = "drop database {};".format(db_name)
        # 先执行查询 再删除
        if not self.database_exist(db_name):
            LogMessage(level=LOG_ERROR, module='Mysql', msg="Dtaabase [{}] doesn't exist".format(db_name))
            cmd_status = False
        else:
            if self.execut(sql):
                # 检查是否被删除
                if self.database_exist(db_name):
                    cmd_status = False

        LogMessage(level=LOG_ERROR, module='Mysql', msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def table_create(self, tb_name, tb_structure, charset=""):
        """
        通过传入表名 表结构 编码格式 创建对应的表
        :param tb_name: 表名
        :param tb_structure: 表结构
        :param charset: 编码格式
        :return: 执行状态 True or False
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        # 命令状态标识
        cmd_status = True
        # 表结构数据拼接字符
        structure_data = ", ".join(["{} {}({})".format(field_name, field_type, field_length)\
                                    for field_name, field_type, field_length in tb_structure])
        # 大小写兼容处理
        structure_data = structure_data.lower()
        # 根据是否传入编码类型 生成对应sql语句
        if not charset:
            sql = "creat table {}({});".format(tb_name, structure_data)
        else:
            sql = "creat table {}({}) charset={};".format(tb_name, structure_data, charset)
        if self.table_exist(tb_name):
            LogMessage(level=LOG_ERROR, module="Mysql", msg=" Table [{}] has been exist ".format(tb_name))
            cmd_status = False
        else:
            if self.execut(sql):
                # 检查表是否创建成功
                if not self.table_exist(tb_name, quiet=True):
                    cmd_status = False
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def table_show(self, quiet=False):
        """
        展示所有表
        :param quiet:静默模式
        :return: 所有表
        """
        sql = "show tables;"
        table_data = self.all_get(sql)
        if not quiet:
            LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, table_data))
        return table_data

    def table_exist(self, tb_name, quiet=True):
        """
        通过传入表名查看表是否存在
        :param tb_name: 表名
        :param quiet: 静默模式
        :return: cmd 命令状态 True or False
        """
        # 命令标识
        cmd_status = True
        table_data = self.table_show(quiet=quiet)
        if table_data:
            tables_str = ",".join([value for table in table_data for key, value in table.items()])
            if tb_name not in tables_str:
                cmd_status = False
            return cmd_status
        else:
            LogMessage(level=LOG_ERROR, module="Mysql", msg="can't connect to MYSQL Server")

    def table_structure(self, tb_name):
        """
        通过表名查看所有表结构
        :param tb_name: 表名
        :return: 表结构
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        sql = "desc {};".format(tb_name)
        table_structure = self.all_get(sql)
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, table_structure))
        return table_structure

    def table_drop(self, tb_name):
        """
        通过表名删除对应的表
        :param tb_name: 表名
        :return: cmd 命令状态 True or False
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        # 命令状态标识
        cmd_status = True
        sql = "drop table {};".format(tb_name)
        # 查询表是否存在 再进行删除
        if not self.table_exist(tb_name):
            LogMessage(level=LOG_ERROR, module="Mysql", msg="Table [{}] doesn't exist".format(tb_name))
            cmd_status = False
        else:
            if self.execut(sql):
                # 检查是否删除
                if self.table_exist(tb_name, quiet=True):
                    cmd_status = False

        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def qyery(self, tb_name, fields='*', condition='', group='', order='', having='', limit='', distinct=False):

        """
        根据传入的具体信息 创建表
        :param tb_name: 表名
        :param fields: 字段名
        :param condition: 限制条件，where+具体内容
        :param group: 分组限制
        :param order: 排序限制
        :param having: 过滤
        :param limit: 限制记录条数
        :param distinct: 去重 默认False
        :return: 查询对应的记录
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        # 命令状态标识
        cmd_status = True
        if group:
            group = "group by" + group.lower()
        if order:
            order = "order by" + order.lower()
        if having:
            having = "having" + having.lower()
        if limit:
            if isinstance(limit, tuple):
                limit = "limit " + str(limit[0]) + ', ' + str(limit[1])
            else:
                limit = 'limit' + str(limit)
            limit = limit.lower()

        if condition:
            condition = "where {}".format(condition)
            condition = condition.lower()
        if distinct:
            sql = "select distinct {} from {} {} {} {} {}".format(fields, tb_name, condition,
                                                                  group, order, having, limit).strip() + ";"
        else:
            sql = "select {} from {} {} {} {} {} {}".format(fields, tb_name, condition,
                                                            group, order, having, limit).strip() + ";"
        result = self.all_get(sql)
        if not result:
            cmd_status = False
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}\n{}".format(sql, result, cmd_status))
        return result

    def insert(self, tb_name, insert_data):
        """
        插入记录 通过传入表名 向指定的表 插入指定记录
        :param tb_name: 表名
        :param insert_data:插入的记录数据
        :return: TRUE or False
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        # 命令状态标识
        cmd_status = True
        # 获取对应的表结构
        table_structure = self.raw_sql("desc {}".format(tb_name))
        table_fields = [field["Field"] for field in table_structure]
        keyworld_list = ['ADD', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ASENSITIVE', 'BEFORE', 'BETWEEN',
                         'BIGINT',
                         'BINARY',
                         'BLOB', 'BOTH', 'BY', 'CALL', 'CASCADE', 'CASE', 'CHANGE', 'CHAR', 'CHARACTER', 'CHECK',
                         'COLLATE',
                         'COLUMN', 'CONDITION', 'CONSTRAINT', 'CONTINUE', 'CONVERT', 'CREATE', 'CROSS', 
                         'CURRENT_DATE', 
                         'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR', 'DATABASE', 'DATABASES', 
                         'DAY_HOUR',
                         'DAY_MICROSECOND', 'DAY_MINUTE', 'DAY_SECOND', 'DEC', 'DECIMAL', 'DECLARE', 'DEFAULT',
                         'DELAYED', 
                         'DELETE',
                         'DESC', 'DESCRIBE', 'DETERMINISTIC', 'DISTINCTROW', 'DIV', 'DOUBLE', 'DROP', 'DUAL',
                         'EACH', 
                         'ELSE', 'ELSEIF', 'ENCLOSED', 'ESCAPED', 'EXISTS', 'EXIT', 'EXPLAIN', 'FALSE', 'FETCH',
                         'FLOAT',
                         'FLOAT4', 
                         'FLOAT8', 'FOR', 'FORCE', 'FOREIGN', 'FROM', 'FULLTEXT', 'GOTO', 'GRANT', 'GRANT', 'GROUP', 
                         'HAVING',
                         'HIGH_PRIORITY', 'HOUR_MICROSECOND', 'HOUR_MINUTE', 'HOUR_SECOND', 'IF', 'IGNORE', 'IN', 
                         'INDEX', 
                         'INFILE', 
                         'INNER', 'INOUT', 'INSENSITIVE', 'INSERT', 'INT', 'INT1', 'INT2', 'INT3', 'INT4', 'INT5',
                         'INT6', 'INT7', 'INT8',
                         'INTEGER',
                         'INTERVAL', 'INTO', 'IS', 'ITERATE', 'JOIN', 'KEY', 'KEYS', 'KILL', 'LABEL', 'LEADING',
                         'LEAVE',
                         'LEFT',
                         'LIKE', 'LIMIT', 'LINEAR', 'LINES', 'LOAD', 'LOCALTIME', 'LOCALTIME', 'LOCK', 'LONG',
                         'LONGBLOB',
                         'LONGTEXT', 'LOOP', 'LOW_PRIORITY', 'MATCH', 'DIV', 'DOUBLE', 'DROP', 'DUAL',
                         'MIDDLEINT', 
                         'MINUTE_MICROSECOND', 'MINUTE_SECOND', 'MOD', 'MODIFIES', 'NATURAL', 'NOT', 
                         'NULL',
                         'NO_WRITE_TO_BINLOG',
                         'NUMERIC', 'NO', 'OPTIMIZE', 'OPTION', 'OPTIONALLY', 'OR', 'ORDER', 'OUT', 'OUTER', 'OUTFILE',
                         'PRECISION', 
                         'PRIMARY', 'PROCEDURE', 'PURGE', 'RAID0', 'RANGE', 'READ', 'READS', 'REAL', 'REFERENCES',
                         'REGEXP', 
                         'RELEASE', 'RENAME', 'REPEAT', 'REPLACE', 'REQUIRE', 'RESTRICT', 'RETURN', 'REVOKE', 'RIGHT',
                         'RLIKE',
                         'SCHEMA', 'SCHEMAS', 'SECOND_MICROSECOND', 'SELECT', 'SENSITIVE', 'SEPARATOR', 'SET', 'SHOW',
                         'SMALLINT',
                         'SPATIAL', 'SPECIFIC', 'SQL', 'SQLEXCEPTION', 'SQLWARNING', 'SQL_BIG_RESULT',
                         'SQL_CALC_FOUND_ROWS', 'SQL_SMALL_RESULT', 'SSL', 'STARTING', 'STRAIGHT_JOIN', 'TABLE',
                         'TERMINATED',
                         'THEN', 'TINYBLOB', 'TINYINT', 'TINYTEXT', 'TO', 'TRAILING', 'TRIGGER', 'TRUE', 'UNDO', 'UNION',
                         'UNIQUE',
                         'UNLOCK', 'UNSIGNED', 'UPDATE', 'USAGE', 'USE', 'USING', 'UTC_DATE', 'UTC_TIME',
                         'UTC_TIMESTAMP',
                         'VALUES',
                         'VARBINARY', 'VARCHAR', 'VARCHARACTER', 'VARYING', 'WHEN', 'WHERE', 'WHILE', 'WITH', 'WRITE',
                         'X509',
                         'XOR', 
                         'YEAR_MONTH', 'ZEROFILL',
                         ]
        for element in table_fields:
            for keyworld in keyworld_list:
                if element == keyworld.lower():
                    table_fields[table_fields.index(element)] = "`{}`".format(element)
                    
        # 对插入的记录数量进行预先查询
        previous_query = self.count_get(tb_name)
        value_str = ", ".join(str(value) for value in insert_data)
        value_str = value_str.lower()
        # 生成完整sql
        sql = "insert into {}({}) values{};".format(tb_name, ", ".join(table_fields).lower(), value_str)
        if self.execut(sql):
            # 对记录数据查询 验证插入是否成功
            last_query = self.count_get(tb_name)
            if last_query['count(*)'] < previous_query['count(*)']:
                cmd_status = False
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def up_date(self, tb_name, update_field, condition):
        """
        更新表 根基表名，向指定的表更新数据
        :param tb_name: 表名
        :param update_field: 更新字段
        :param condition: 更新字段所在记录
        :return: True of False
        """
        # 大小写兼容处理
        tb_name = tb_name.lower()
        update_field = update_field.lower()
        condition = condition.lower()
        # 命令状态标识
        cmd_status = True
        # 对更新记录预先查询

        # 对插入的记录数量进行预先查询
        query_condition = " and ".join(update_field.split(',')).lower()
        previous_query = self.count_get(tb_name, condition=query_condition)
        # 生成完整sql
        sql = "update {} set {} where {};".format(tb_name, update_field, condition)
        if self.execut(sql):
            # 对记录数据查询 验证插入是否成功
            last_query = self.count_get(tb_name, condition=query_condition)
            if last_query['count(*)'] < previous_query['count(*)']:
                cmd_status = False
        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def delete(self, tb_name, condition):
        """
        删除记录 根据传入表名 删除对应条件记录
        :param tb_name: 表名
        :param condition: 记录条件
        :return: True of False
        """

        # 大小写兼容处理
        tb_name = tb_name.lower()
        condition = condition.lower()
        # 命令状态标识
        cmd_status = True
        # 查询条件
        query_condition = " and ".join(condition.split(','))
        # 生成完整sql
        sql = "delete from {} where {};".format(tb_name, condition)
        self.execut(sql)
        # 对记录数量再次查询
        last_query = self.count_get(tb_name, condition=query_condition)

        if last_query['count(*)'] > 1:
            cmd_status = False

        LogMessage(level=LOG_INFO, module="Mysql", msg="{}\n{}".format(sql, cmd_status))
        return cmd_status

    def close(self):
        """
        关闭连接
        :return:
        """
        if self.mysql:
            self.mysql.cursor().close()
            self.mysql.close()


if __name__ == '__main__':
    msg = MsgCenter(testcase_name="Mysql")
    LogMessage(level=LOG_INFO, module="Mysql", msg=" check {}".format(">>>>>>>"))
    mysql = Mysql()
