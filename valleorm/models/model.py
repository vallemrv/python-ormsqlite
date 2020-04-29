# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0

import sqlite3
import json
import base64

from . import constant
from .fields import *
from .relatedfields import *



class Model(object):

    def __init__(self, schema=None, **options):

        self.estado = constant.STATE_NEW
        self.lstCampos = []
        self.foreingKeys = []
        self.table_name = Utility.default_tb_name(self.__class__)
        self.dbName = Utility.default_db_name(self.__class__)
        self.schema= schema
        self.id = -1
        self.__crea_tb_schemas__()

        if not self.schema:
            self.__load_models__()

        if self.schema:
            self.__init_model__()
        elif not type(self) is Model:
            self.__init_campos__()
       
        for k, v in options.items():
            setattr(self, k, v)

    def __setattr__(self, attr, value):
        
        if hasattr(self, 'lstCampos') and self.lstCampos and attr in self.lstCampos:
            field = super(Model, self).__getattribute__(attr)
            field.set_dato(value)
        else:
            super(Model, self).__setattr__(attr, value)

    def __getattribute__(self, attr):
        value = super(Model, self).__getattribute__(attr)
        if hasattr(value, 'get_dato'):
            return value.get_dato()

        return value
       

    def __crea_tb_schemas__(self):
        IDprimary = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        sql = "CREATE TABLE IF NOT EXISTS django_models_db (%s, table_name TEXT UNIQUE, model TEXT);"
        sql = sql % IDprimary
        Utility.execute_query(sql, self.dbName)

    #Introspection of  the models
    def __init_model__(self):
        self.lstCampos = []
        if "fields" in self.schema:
            for m in self.schema.get("fields"):
                if "tipo_class" in m  and "tipo" in m and "field_name" in m:
                    field_class = create_field_class(m)
                    setattr(self, m.get("field_name"), field_class)
                    self.lstCampos.append(m.get("field_name"))     
                else:
                    raise Exception('Error al inicial el modelo de datos')

        

        if "relationship" in self.schema:
            for m in self.schema.get("relationship"):
                if "class_name" in m  and "field_name" in  m:
                    field_name = m.get("field_name")
                    rel_new = create_relation_class(m, self)
                    setattr(self, field_name, rel_new)
                    if m.get("class_name") == "ForeignKey":
                        id_field_name = rel_new.id_field_name
                        setattr(self, id_field_name, IntegerField())
                        self.lstCampos.append(id_field_name)
                   
                else:
                    raise Exception("Error al contruir el modelo de datos, FATAL")

    #Introspection of the inherited class
    def __init_campos__(self):
        self.schema= {'fields':[],'relationship':[]}
        for key in dir(self):
            field =  super(Model, self).__getattribute__(key)
            tipo_class = ""
            if hasattr(field, 'tipo_class'):
                tipo_class = field.tipo_class
            if tipo_class == constant.TIPO_CAMPO:
                self.schema["fields"].append(field.get_serialize_data(key))
                self.lstCampos.append(field.field_name)
            elif tipo_class == constant.TIPO_RELATION:
                serialize_data = field.get_serialize_data(key)
                field.main_model_class = self
                if field.class_name == "ForeignKey":
                    id_field_name = field.id_field_name
                    setattr(self, id_field_name, IntegerField())
                    self.foreingKeys.append(field.get_sql_pk())
                    serialize_data["othermodel"] = field.related_class.table_name
                    self.schema["relationship"].append(serialize_data)
                    self.lstCampos.append(field.id_field_name)
                if field.class_name == "ManyToMany":
                    self.schema["relationship"].append(serialize_data)
                    self.__crear_tb_nexo__(field)

       
        self.__save_schema__(base64.b64encode(json.dumps(self.schema).encode()))   
        self.__create_if_not_exists__()
        self.__init_model__()

    def __create_if_not_exists__(self):
        fields = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for key in self.lstCampos:
            field  = super(Model, self).__getattribute__(key)
            fields.append(u"'{0}' {1}".format(key, field.toQuery()))

        frgKey = "" if len(self.foreingKeys)==0 else u", {0}".format(", ".join(self.foreingKeys))

        values = ", ".join(fields)
        sql = u"CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            self.table_name,
                                                            frgKey)
        Utility.execute_query(sql, self.dbName)

    def __save_schema__(self, strModel):
        sql = u'INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ("{0}","{1}");'
        sql = sql.format(self.table_name, strModel)
        Utility.execute_query(sql, self.dbName)


    def __crear_tb_nexo__(self, relation):
        sql = relation.get_sql_tb_nexo()
        Utility.execute_query(sql, self.dbName)

    def __getenerate_joins__(self, joins):
        strJoins = []
        for j in joins:
            sql = j if j.startswith("INNER") else "INNER JOIN "+j
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)

    def __load_models__(self):
        sql = 'SELECT model FROM django_models_db WHERE table_name="%s"' % self.table_name
        reg, d = Utility.execute_select(sql, self.dbName)
        if reg:
           self.schema= json.loads(base64.b64decode(eval(reg[0][0])))

    def __cargar_datos__(self, **datos):
        for k, v in datos.items():
            if k=="id":
                self.id = v
            else:
                setattr(self, k, v)
                self.lstCampos.append(k)

   
    def appned_fields(self, fields, update=False,):
        if not self.schema:
           self.schema= {'fields':[],'relationship':[]}
        modelfield = self.schema["fields"]
        for field in fields:
            key = field.field_name
            search = filter(lambda field: field['field_name'] == key, modelfield)
            if len(search) <= 0:
                self.schema["fields"].append(field.get_serialize_data(field.field_name))
                setattr(self, key, field)
                self.lstCampos.append(key)
                self.__save_schema__(base64.b64encode(json.dumps(self.schema)))
                if update:
                    Model.alter(self.dbName, self.table_name, field)

    def append_relation(self, rel_new):
        relationship = self.schema["relationship"]
        key = rel_new.field_name
        if key != "model":
            search = list(filter(lambda rel: rel['field_name'] == key, relationship))
            if len(search) <= 0:
                self.schema["relationship"].append(rel_new.get_serialize_data(rel_new.field_name))
                setattr(self, key, rel_new)
                self.__save_schema__(base64.b64encode(json.dumps(self.schema).encode()))

    def save(self, **kargs):
        self.__cargar_datos__(**kargs)
        self.id = -1 if self.id == None else self.id

        if self.estado == constant.STATE_NEW:
            keys =[]
            vals = []
            for key in self.lstCampos:
                val = super(Model, self).__getattribute__(key)
                keys.append(key)
                vals.append(val.get_pack_dato())
            cols = ", ".join(keys)
            values = ", ".join(vals)
            sql = u"INSERT INTO {0} ({1}) VALUES ({2});".format(self.table_name,
                                                                   cols, values)
        else:
            vals = []
            for key in self.lstCampos:
                val = super(Model, self).__getattribute__(key)

                vals.append(u"{0} = {1}".format(key, val.get_pack_dato()))
            values = ", ".join(vals)
            sql = u"UPDATE {0}  SET {1} WHERE id={2};".format(self.table_name,
                                                              values, self.id);
        db = sqlite3.connect(self.dbName)
        cursor = db.cursor()
        cursor.execute(sql)
        if self.id == -1:
            self.id = cursor.lastrowid
        db.commit()
        db.close()

    def delete(self):
        self.id = -1 if self.id == None else self.id
        sql = u"DELETE FROM {0} WHERE id={1};".format(self.table_name, self.id)
        Utility.execute_query(sql, self.dbName)
        self.id = -1
        self.estado = constant.STATE_DELETE
        return "success"

    def toJSON(self):
        js = self.toDICT()
        return json.dumps(js, ensure_ascii=False)

    def toDICT(self):
        if self.id > 0:
            js = {"id": self.id}
        else:
            js = {}
        for key in self.lstCampos:
            field = super().__getattribute__(key)
            js[key] = field.get_str_value()
        return js
    
    
    @classmethod
    def find(cls, **condition):
        sql = "SELECT * FROM {0} {1};".format(Utility.default_tb_name(cls), Utility.decode_condition(cls, **condition))
        reg, d = Utility.execute_select(sql, Utility.default_db_name(cls))
        registros = []
        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = cls()
            obj.__cargar_datos__(**res)
            registros.append(obj)

        return registros
               

    
    @classmethod
    def empty(cls):
        Utility.execute_query("DELETE FROM %s;" % Utility.default_tb_name(cls))


    @classmethod
    def first(cls, **condition):
        condition["limit"] = 1
        reg = cls.find(**condition)
        if len(reg) > 0:
            return  reg[0]
            

    @classmethod
    def getByPk(cls, pk):
        sql = u"SELECT * FROM {0} WHERE id={1};".format(Utility.default_tb_name(cls), pk)
        db = sqlite3.connect(Utility.default_db_name(cls))
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            req_cls = cls()
            req_cls.__cargar_datos__(**res)
            return req_cls
        return None
        

    @classmethod
    def get_model(cls):
        sql = "SELECT model FROM django_models_db WHERE table_name='%s';" % Utility.default_tb_name(cls)
        reg, c = Utility.execute_select(sql, Utility.default_db_name(cls))
        if reg:
            return json.loads(base64.b64decode(reg[0].decode()))

    
    @classmethod
    def delete_row(cls, **condition):
        sql = "DELETE FROM {0} {1};".format(Utility.default_tb_name(cls), Utility.decode_condition(cls, **condition))
        Utility.execute_query(sql, Utility.default_db_name(cls))
        
        
    @staticmethod
    def drop_db(dbName):
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
    def exits_table(table_name, dbName='db.sqlite3'):
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
    def alter_model(table_name, schema, dbName='db.sqlite3'):
        strModel = base64.b64encode(json.dumps(schema))
        sql = u'INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ("{0}","{1}");'
        sql = sql.format(table_name, strModel)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter_constraint(table_name, colum_name, parent, dbName='db.sqlite3', delete=constant.CASCADE):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} INTEGER REFERENCES {2}(id) {3};"
        sql = sql.format(table_name, colum_name, parent, delete)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter(field, dbName='db.sqlite3'):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} {2};"
        sql = sql.format(field.table_name, field.field_name, field.toQuery())
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()


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
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(query)
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
    def decode_condition(cls, **condition):
        query = ""
        op = ""
        for k, v in condition.items():
            if k in ['limit', 'offset', 'order_by']:
                op += "%s %s" % (k,v)
            elif hasattr(cls, k):
                field = getattr(cls, k)   
                if hasattr(field, "get_pack_dato"):
                    field.set_dato(v)
                    query += " %s=%s " % (k, field.get_pack_dato())
            elif k in ["id", "pk"]:
                     query += "id=%s" % v
            elif "__start" in k:
                query += " {1} LIKE '%{0}' ".format(v, k.split("__")[0])
            elif "__end" in k:
                query += " {1} LIKE '{0}%' ".format(v, k.split("__")[0])
            elif "__contain" in k:
                query += " {1} LIKE '%{0}%' ".format(v, k.split("__")[0])

        if query != "":
            query = "WHERE %s" % query

        return "{0} {1}".format(query, op)


