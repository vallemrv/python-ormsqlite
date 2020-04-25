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
    def __init__(self, table_name=None, dbName="db.sqlite3",
                 model=None, alter=False, **options):
        self.lstCampos = []
        self.columns = "*"
        self.foreingKeys = []
        self.ID = -1
        self.table_name = table_name
        if self.table_name is None:
            self.table_name = self.__class__.__name__.lower()
        self.dbName = dbName
        self.model = model
        self.__crea_tb_schemas__()

        if not self.model:
            self.__load_models__()


        if self.model and not alter:
            self.__init_model__()
        elif not type(self) is Model:
            self.__init_campos__()

        for k, v in options.items():
            isWordReserver = k == 'columns' or k == 'limit' or k == 'offset'
            isWordReserver = isWordReserver or k == 'query' or k == 'order'
            isWordReserver = isWordReserver or k == 'joins' or k == 'group'
            if isWordReserver:
                self.load_first_by_query(**options)
            elif k == 'pk':
                self.load_by_pk(v)
            else:
                setattr(self, k, v)

    def __setattr__(self, attr, value):
        es_dato_simple = type(value) in (str, int, bool, float)
        es_dato_simple = es_dato_simple and hasattr(self, 'lstCampos') and attr in self.lstCampos
        if es_dato_simple:
            field = super(Model, self).__getattribute__(attr)
            field.set_dato(value)
        else:
            super(Model, self).__setattr__(attr, value)

    def __getattribute__(self, attr):
        try:
            value = super(Model, self).__getattribute__(attr)
            if hasattr(value, 'tipo_class') and value.tipo_class == constant.TIPO_CAMPO:
                return value.get_dato()

            return value
        except AttributeError:
            return None

    def __crea_tb_schemas__(self):
        IDprimary = "ID INTEGER PRIMARY KEY AUTOINCREMENT"
        sql = "CREATE TABLE IF NOT EXISTS django_models_db (%s, table_name TEXT UNIQUE, model TEXT);"
        sql = sql % IDprimary
        self.execute(sql)

    #Introspection of  the models
    def __init_model__(self):
        if "fields" in self.model:
            for m in self.model.get("fields"):
                if "tipo_class" in m  and "tipo" in m and "field_name" in m:
                    field_class = create_field_class(m)
                    setattr(self, m.get("field_name"), field_class)
                    self.lstCampos.append(m.get("field_name"))
                else:
                    raise Exception('Error al inicial el modelo de datos')

        if "relationship" in self.model:
            for m in self.model.get("relationship"):
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
        self.model = {'fields':[],'relationship':[]}
        for key in dir(self):
            field =  super(Model, self).__getattribute__(key)
            tipo_class = ""
            if hasattr(field, 'tipo_class'):
                tipo_class = field.tipo_class
            if tipo_class == constant.TIPO_CAMPO:
                self.model["fields"].append(field.get_serialize_data(key))
                self.lstCampos.append(key)
            elif tipo_class == constant.TIPO_RELATION:
                self.model["relationship"].append(field.get_serialize_data(key))
                field.main_model_class = self
                if field.class_name == "ForeignKey":
                    id_field_name = field.id_field_name
                    setattr(self, id_field_name, IntegerField())
                    self.lstCampos.append(id_field_name)
                    self.foreingKeys.append(field.get_sql_pk())
                if field.class_name == "ManyToMany":
                    self.__crear_tb_nexo__(field)

        self.__save_schema__(base64.b64encode(json.dumps(self.model)))
        self.__create_if_not_exists__()
        self.__init_model__()

    def __create_if_not_exists__(self):
        fields = ["ID INTEGER PRIMARY KEY AUTOINCREMENT"]
        for key in self.lstCampos:
            field  = super(Model, self).__getattribute__(key)
            fields.append(u"'{0}' {1}".format(key, field.toQuery()))

        frgKey = "" if len(self.foreingKeys)==0 else u", {0}".format(", ".join(self.foreingKeys))

        values = ", ".join(fields)
        sql = u"CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            self.table_name,
                                                            frgKey)
        self.execute(sql)

    def __save_schema__(self, strModel):
        sql = u"INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ('{0}','{1}');"
        sql = sql.format(self.table_name, strModel)
        self.execute(sql)

    def __crear_tb_nexo__(self, relation):
        sql = relation.get_sql_tb_nexo()
        self.execute(sql)

    def __getenerate_joins__(self, joins):
        strJoins = []
        for j in joins:
            sql = j if j.startswith("INNER") else "INNER JOIN "+j
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)

    def __load_models__(self):
        sql = "SELECT model FROM django_models_db WHERE table_name='%s'" % self.table_name
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            self.model = json.loads(base64.b64decode(reg[0]))

    def __cargar_datos__(self, **datos):
        for k, v in datos.items():
            if k=="ID":
                self.ID = v
            else:
                setattr(self, k, v)
                self.lstCampos.append(k)

    def appned_fields(self, fields, update=False,):
        if not self.model:
            self.model = {'fields':[],'relationship':[]}
        modelfield = self.model["fields"]
        for field in fields:
            key = field.field_name
            search = filter(lambda field: field['field_name'] == key, modelfield)
            if len(search) <= 0:
                self.model["fields"].append(field.get_serialize_data(field.field_name))
                setattr(self, key, field)
                self.lstCampos.append(key)
                self.__save_schema__(base64.b64encode(json.dumps(self.model)))
                if update:
                    Model.alter(self.dbName, self.table_name, field)

    def append_relation(self, rel_new):
        relationship = self.model["relationship"]
        key = rel_new.field_name
        if key != "model":
            search = filter(lambda rel: rel['field_name'] == key, relationship)
            if len(search) <= 0:
                self.model["relationship"].append(rel_new.get_serialize_data(rel_new.field_name))
                setattr(self, key, rel_new)
                self.__save_schema__(base64.b64encode(json.dumps(self.model)))

    def save(self, **kargs):
        self.__cargar_datos__(**kargs)
        self.ID = -1 if self.ID == None else self.ID

        if self.ID == -1:
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
            sql = u"UPDATE {0}  SET {1} WHERE ID={2};".format(self.table_name,
                                                                 values, self.ID);
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        if self.ID == -1:
            self.ID = cursor.lastrowid
        db.commit()
        db.close()

    def delete(self):
        self.ID = -1 if self.ID == None else self.ID
        sql = u"DELETE FROM {0} WHERE ID={1};".format(self.table_name, self.ID)
        self.execute(sql)
        self.ID = -1

    def empty(self):
        self.ID = -1;
        self.execute("DELETE FROM %s;" % self.table_name)

    def getAll(self, **condition):
        self.columns = "*" if not 'columns' in condition else ", ".join(condition.get("columns"))
        order = "" if not 'order' in condition else "ORDER BY %s" % str(condition.get('order'))
        query = "" if not 'query' in condition else "WHERE %s" % str(condition.get("query"))
        limit = "" if not 'limit' in condition else "LIMIT %s" % condition.get("limit")
        offset = "" if not 'offset' in condition else "OFFSET %s" % condition.get('offset')
        joins = "" if not 'joins' in condition else self.__getenerate_joins__(condition.get("joins"))
        group = "" if not 'group' in condition else "GROUP BY %s" % condition.get("group")
        sql = u"SELECT {0} FROM {1} {2} {3} {4} {5} {6} {7};".format(self.columns, self.table_name,
                                                         joins, query, order, group, limit, offset)

                                                    
        return self.select(sql)

    def select(self, sql):
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()

        cursor.execute(sql)
        reg = cursor.fetchall()
        d = cursor.description
        db.commit()
        db.close()
        registros = []

        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = Model(table_name=self.table_name, dbName=self.dbName)
            obj.__cargar_datos__(**res)

            registros.append(obj)

        return registros

    def execute(self, query):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(self.dbName)
            cursor= db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(query)
            db.commit()
            db.close()

    def load_first_by_query (self, **condition):
        reg = self.getAll(**condition)
        if len(reg) > 0:
            self.__cargar_datos__(**reg[0].toDICT())

    def load_by_pk(self, pk):
        sql = u"SELECT * FROM {0} WHERE ID={1};".format(self.table_name, pk)
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            self.__cargar_datos__(**res)

    def toJSON(self):
        js = self.toDICT()
        return json.dumps(js, ensure_ascii=False)

    def toDICT(self):
        if self.ID > 0:
            js = {"ID": self.ID}
        else:
            js = {}
        for key in self.lstCampos:
            v =  getattr(self, key)
            if self.columns == "*":
                if not (v == "None" or v is None):
                    js[key] = v
            elif key in self.columns and not (v == "None" or v is None):
                js[key] = v

        return js

    @classmethod
    def get_model(cls, table_name=None, dbName='db.sqlite3'):
        if not table_name:
            table_name = cls.__name__.lower()
        sql = "SELECT model FROM django_models_db WHERE table_name='%s'" % table_name
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            return json.loads(base64.b64decode(reg[0]))

    @staticmethod
    def to_array_dict(registros):
        lista = []
        for r in registros:
            reg = r.toDICT()
            lista.append(reg)

        return lista

    @staticmethod
    def remove_rows(registros):
        lista = []
        for r in registros:
            lista.append({'ID': r.ID, 'success': True})
            r.remove()
        return lista

    @staticmethod
    def serialize(registros):
        lista = []
        for r in registros:
            reg = {}
            reg["table_name"] = r.table_name
            reg["dbName"] = r.dbName
            reg["datos"] = r.toDICT()
            lista.append(reg)

        return json.dumps(lista)

    @staticmethod
    def deserialize(dbJSON):
        lista = json.loads(dbJSON)
        registros = []
        for l in lista:
            obj = Model(table_name=l["table_name"], dbName=l["dbName"])
            obj.__cargar_datos__(**l["datos"])
            registros.append(obj)

        return registros

    @staticmethod
    def drop_db(dbName):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%sqlite%';"
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        for r in reg:
            cursor.execute("DROP TABLE %s" % r)
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
    def alter_model(table_name, model, dbName='db.sqlite3'):
        strModel = base64.b64encode(json.dumps(model))
        sql = u"INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ('{0}','{1}');"
        sql = sql.format(table_name, strModel)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter_constraint(table_name, colum_name, parent, dbName='db.sqlite3', delete=constant.CASCADE):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} INTEGER REFERENCES {2}(ID) {3};"
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
