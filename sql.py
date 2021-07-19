import sqlite3

from log import info, error

DB_NAME = "default.db"


class SQLHelper:

    def __init__(self, db_name=DB_NAME):
        self.connect = sqlite3.connect(db_name)
        self.cursor = self.connect.cursor()
        info("数据库初始化成功")

    '''
    创建表
    :table_name 表名
    :field 字段列表
    '''
    def create_table(self, table_name, field):
        if not isinstance(field, dict):
            raise Exception("error: field 必须是字典")
        try:
            fields = ",".join([k + " " + v for k, v in field.items()])
            sql = f"create table if not exists {table_name}({fields});"
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as ex:
            error("数据库表创建失败 sql={0} ex={1}".format(sql, ex))
            return False

    '''
    插入数据
    :table_name 表名
    :data 要插入的数据
    '''
    def insert_data(self, table_name, data):
        if not isinstance(data, dict):
            raise Exception("error: data 必须是字典")
        try:
            keys = ",".join(list(data.keys()))
            values = ",".join([f"'{x}'" for x in list(data.values())])
            sql = f"insert into {table_name} ({keys}) values ({values});"
            self.cursor.execute(sql)
            return True
        except Exception as ex:
            error("数据插入失败 sql={0} ex={1}".format(sql, ex))
            return False
        finally:
            self.connect.commit()

    '''
    更新数据
    :table_name 表名
    :data 要更新的数据
    '''
    def update_data(self, table_name, data, id):
        if not isinstance(data, dict):
            raise Exception("error: data 必须是字典")
        if not isinstance(id, int):
            raise Exception("error: id 必须是int")
        try:
            keys = ",".join(list(data.keys()))
            values = ",".join([f"'{x}'" for x in list(data.values())])
            sql = f"update {table_name} set {keys}={values} where id={id};"
            self.cursor.execute(sql)
            return True
        except BaseException as ex:
            error("数据更新失败 sql={0} ex={1}".format(sql, ex))
            return False
        finally:
            self.connect.commit()

    '''
    查询表数据
    :table_name 表名
    '''
    def query_data(self, table_name):
        try:
            sql = f"select * from {table_name};"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as ex:
            error("数据更新失败 sql={0} ex={1}".format(sql, ex))
            return []

    '''
    关闭数据库
    '''
    def close(self):
        self.cursor.close()
        self.connect.close()


# db = SQLHelper()
# db.create_table("mogoo", {
#     "id": "integer primary key autoincrement",
#     "key": "text"
# })
# db.insert_data("mogoo", {
#     "key": "goo"
# })
# db.update_data("mogoo", {
#     "key": "qwe"
# }, 1)
# for value in db.query_data("mogoo"):
#     print(value)
# db.close()
