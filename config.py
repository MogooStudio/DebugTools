import json
import os
import pickle

from log import info, error

'''
序列化/反序列化：json
'''


class JsonConfig:

    def __init__(self, file):
        self.file = file
        info("初始化config file={0}".format(self.file))

    def dumps(self, data):
        try:
            return json.dumps(data)
        except Exception as ex:
            error("序列化失败 ex={0}".format(str(ex)))

    def loads(self, jsonString):
        try:
            return json.loads(jsonString)
        except Exception as ex:
            error("反序列化失败 ex={0}".format(str(ex)))

    def write_file(self, data):
        if self.file is not None:
            with open(self.file, 'w') as fp:
                json.dump(data, fp)
        else:
            raise Exception("文件未定义 self.file={0}".format(self.file or ""))

    def read_file(self):
        if not os.path.exists(self.file) or not self.getFileContent():
            return None
        if self.file is not None:
            with open(self.file, 'r') as fp:
                return json.load(fp)
        else:
            raise Exception("文件不存在 self.file={0}".format(self.file or ""))

    def getFileContent(self):
        if self.file is not None and os.path.exists(self.file):
            with open(self.file, 'r') as fp:
                return fp.read()
        return None


'''
序列化/反序列化：Pickle
'''


class PickleConfig:

    def __init__(self, file, obj=object()):
        self.file = file
        self.obj = obj
        self.byteString = self.dumps(self.obj)
        info("初始化config成功 file={0} byteString={1}".format(self.file, self.byteString))

    def dumps(self, obj=None):
        try:
            return pickle.dumps(self.obj if obj is None else obj)
        except Exception as ex:
            error("序列化失败 ex={0}".format(str(ex)))

    def loads(self, byteString=None):
        try:
            return pickle.loads(self.byteString if byteString is None else byteString)
        except Exception as ex:
            error("反序列化失败 ex={0}".format(str(ex)))

    def write_file(self, obj=None):
        if self.file is not None:
            with open(self.file, 'wb') as fp:
                pickle.dump(self.obj if obj is None else obj, fp)
        else:
            raise Exception("文件未定义 self.file={0}".format(self.file or ""))

    def read_file(self):
        if self.file is not None and os.path.exists(self.file):
            with open(self.file, 'rb') as fp:
                return pickle.load(fp)
        else:
            raise Exception("文件不存在 self.file={0}".format(self.file or ""))


class Student(object):

    def __init__(self, name, age, sno):
        super(Student, self).__init__()
        self.name = name
        self.age = age
        self.sno = sno

    def getStr(self):
        return {
            "name": self.name,
            "age": self.age,
            "sno": self.sno,
        }


# config = JsonConfig('test.json',
#                     {'a': 'str中国', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g': (4, 5, 6)})
#
# # 序列化
# jsonStr = config.dumps()
# print("序列化数据：" + jsonStr)
# jsonStr = config.dumps({'a1': 'hello', 'b2': 20, 'c3': False})
# print("序列化数据(带参数)：" + jsonStr)
#
# # 反序列化
# data = config.loads()
# print("反序列化数据：" + str(data))
# data = config.loads(jsonStr)
# print("反序列化数据(带参数)：" + str(data))
#
# # 序列化数据（字典）写入文件
# config.write_file()
# print("序列化数据到文件：" + config.getFileContent())
# config.write_file({'a1': 'hello', 'b2': 20, 'c3': False})
# print("序列化数据到文件(带参数)：" + config.getFileContent())
#
# # 从文件读取并反序列化数据（字典）
# data = config.read_file()
# print("读取文件内容反序列化：" + str(data))
#
# stu = Student('Tom', 19, 1)
# stu1 = Student('Jack', 21, 2)
#
# pickleConfig = PickleConfig("test.data", stu)
#
# # 序列化
# byteStr = pickleConfig.dumps()
# print("序列化数据：" + str(byteStr))
# byteStr = pickleConfig.dumps(stu1)
# print("序列化数据(带参数)：" + str(byteStr))
#
# # 反序列化
# data = pickleConfig.loads()
# print("反序列化数据：" + str(data))
# data = pickleConfig.loads(byteStr)
# print("反序列化数据(带参数)：" + str(data))
#
# # 序列化数据（自定义类）写入文件
# pickleConfig.write_file()
# pickleConfig.write_file(stu1)
#
# # 从文件读取并反序列化数据（自定义类）
# data = pickleConfig.read_file()
# print("读取文件内容反序列化：" + str(data.getStr()))

