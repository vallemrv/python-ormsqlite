import sqlite3
import base64
from . import constant


class Q(object):
    def __init__(self, **kwargs):
        self.query, op = Utility.split_condition(**kwargs)
        
    def __str__(self):
        return " AND ".join(self.query)

    def __or__(self, other):
        if type(other) == dict:
            other = other["query"]
        return {"query": str(self) + " OR " + str(other)}
    
    def __and__(self, other):
        if type(other) == dict:
            other = other["query"]
        return {"query": str(self) + " AND " + str(other)}


class Utility:
    
    @staticmethod
    def default_tb_name(cls):
        if hasattr(cls, "TB_NAME"):
            return cls.TB_NAME
        else:
            return cls.__name__.lower()

    @staticmethod
    def default_db_name(cls):
        if hasattr(cls, "DB_NAME"):
            return cls.DB_NAME
        else:
            return "db.sqlite3"

    @staticmethod
    def execute_query(query, db_name):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(db_name)
            cursor= db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
    
    @staticmethod
    def execute_multiple_query(query, db_name):
        db = sqlite3.connect(db_name)
        for q in query:
            if sqlite3.complete_statement(q):
                cursor= db.cursor()
                cursor.execute(q)

        db.commit()
        db.close()
        
    @staticmethod
    def execute_select(sql, db_name):
        db = sqlite3.connect(db_name)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        d = cursor.description
        db.commit()
        db.close()
        registros = []
        return reg, d

    @staticmethod
    def decode_condition(cls, *args, **kwargs):
        query = []
        op = ""
        for arg in args:
            if type(arg) == dict:
                kwargs.update(arg)
        query, op = Utility.split_condition(**kwargs)

        if query != "":
            query = "WHERE %s" % " AND ".join(query)

        
        return "{0} {1}".format(query, op)

    @staticmethod
    def split_condition(**kwargs):
        query = []
        op = ""
        
        for k, v in kwargs.items():
            if "__" in k:
                os = k.split("__")
                field = os[0]
                action = os[1]
                if action == "between": 
                    v1, v2 = v
                    if type(v1) == str and type(v2) == str:
                        v1 = "'%s'" % v1
                        v2 = "'%s'" % v2
                    query.append(" {0} BETWEEN {1}  AND {2} ".format(field, v1, v2))
                elif action == "gte":
                    if type(v) == str:
                        v = "'%s'" % v
                    query.append(" {1} >= {0} ".format(v, field))
                elif action ==  "lte":
                    if type(v) == str:
                        v = "'%s'" % v
                    query.append(" {1} <= {0} ".format(v, field))
                elif action == "start":
                    query.append(" {1} LIKE '{0}%' ".format(v, field))
                elif action == "end":
                    query.append(" {1} LIKE '%{0}' ".format(v, field))
                elif action == "contain":
                    query.append(" {1} LIKE '%{0}%' ".format(v, field))     
            elif "query" in k:
                query.append(v)
            elif k in ['limit', 'offset', 'order']:
                if k == 'order':
                    k = "ORDER BY"
                op += " %s %s " % (k,v)
            elif k in ["id", "pk"]:
                query.append("id=%s" % v)
            else:
                if type(v) == str:
                    v = "'%s'" % v
                query.append(" %s=%s " % (k, v))
        return query, op

    @staticmethod
    def drop_db(dbName="db.sqlite3"):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%sqlite%';"
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        for r in reg:
            cursor.execute("DROP TABLE %s;" % r)
        db.commit()
        db.close()

    @staticmethod
    def exists_table(table_name, dbName):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % table_name
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None

    @staticmethod
    def alter_model(table_name, schema, dbName):
        import json
        strModel = base64.b64encode(json.dumps(schema))
        sql = u'INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ("{0}","{1}");'
        sql = sql.format(table_name, strModel)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

   
