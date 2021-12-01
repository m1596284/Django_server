# -*- coding: UTF-8 -*-
import sqlite3
from pathlib import Path
from py_logging import py_logger

pyPath = Path(__file__).parent.parent
# log = py_logger("a", dir_path=f"{pyPath}/log",file_name="sqlite_CRUD")

class Database:
    def __init__(self, **kwargs):
        self.db_path = kwargs.get('db_path')
        self._db = sqlite3.connect(self.db_path)
        self._db.row_factory = sqlite3.Row
        # log.debug(f"connect db: {self.db_path}")

    def use_table(self,table_name):
        self.table = table_name

    def sql_do(self, sql, *params):
        self._db.execute(sql, params)
        self._db.commit()

    def create_table(self,table_name,title_type_dict):
        # log.debug(f"{table_name}")
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for thing in title_type_dict:
            sql = f"{sql}{thing} {title_type_dict[thing]},"
            # log.debug(f"{thing}:{title_type_dict[thing]}")
        sql = f"{sql[:-1]});"
        self._db.execute(sql)
        # log.debug(sql)
        # self._db.execute(
        #                 f"""CREATE TABLE IF NOT EXISTS {table_name} (
        #                     id integer PRIMARY KEY,
        #                     name text NOT NULL,
        #                     priority integer,
        #                     project_id integer NOT NULL,
        #                     status_id integer NOT NULL,
        #                     begin_date text NOT NULL,
        #                     end_date text NOT NULL,
        #                     FOREIGN KEY (project_id) REFERENCES projects (id)
        #                     );"""
        #                 )

    def create(self,**kwargs):
        cols = f""
        values = f""
        for thing in kwargs:
            cols = f"{cols}{thing},"
            values = f"{values}'{kwargs[thing]}',"
        sql = f"INSERT INTO {self.table} ({cols[:-1]}) VALUES ({values[:-1]});"
        # sql = "INSERT INTO IU_line_bot_oo_table (id,group,url) VALUES ('0','12','0');"
        # log.debug(f"{sql}")
        self._db.execute(sql)
        self._db.commit()
    
    def read_all(self):
        sql = f"SELECT * FROM {self.table};"
        cursor = self._db.execute(sql)
        return cursor.fetchall()

    def read_column(self, column):
        sql = f"SELECT {column} FROM {self.table};"
        cursor = self._db.execute(sql)
        return cursor.fetchall()

    def read(self,**kwargs):
        where = kwargs.get("where","None")
        sql = f"SELECT * FROM {self.table} WHERE {where};"
        cursor = self._db.execute(sql)
        return cursor.fetchall()

    def update(self, **kwargs):
        values = f""
        where = kwargs.get("where","None")
        for thing in kwargs:
            if thing !="where":
                values = f"{values}{thing}='{kwargs[thing]}',"
        if where == "None":
            sql = f"UPDATE {self.table} SET {values[:-1]};"
        else:
            sql = f"UPDATE {self.table} SET {values[:-1]} WHERE {where};"
        self._db.execute(sql)
        self._db.commit()

    def delete_all(self):
        sql = f"DELETE FROM {self.table};"
        self._db.execute(sql)
        self._db.commit()
        
    def delete(self,**kwargs):
        where = kwargs.get("where","None")
        sql = f"DELETE FROM {self.table} WHERE {where};"
        self._db.execute(sql)
        self._db.commit()

    def close(self):
        self._db.close()
        # log.debug(f"close db: {self.db_path}")

if __name__ == "__main__": 
    pass
    db_path = f"{pyPath}/db.sqlite3"
    db = Database(db_path = f"{db_path}", table = 'test2')
    # title_type_dict = {
    #     "id":"integer",
    #     "name":"text",
    #     "url":"text",
    # }
    # db.create_table("test2",title_type_dict)
    db.delete_all()
    db.create(id=0,name=0,url=0)
    # db.update(id=0, url="http://ssdddss",where="id='0' AND name='test_name'")
    # a = db.read(where="id='999'")
    # a = db.read_all(where="id='999'")
    # for thing in a:
    #     print(thing[2])
    # log.debug(a[2])
    # db.delete(where="id='0'")
    # db.delete_all()
    db.close()
