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
from .tools import Utility



class Model(object):

    def __init__(self, schema=None, **options):

        self.estado = constant.STATE_NEW
        self.lstCampos = []
        self.table_name = Utility.default_tb_name(self.__class__)
        self.dbName = Utility.default_db_name(self.__class__)
        self.schema= schema
        self.id = -1
        if not schema:
            self.schema = self.__class__.get_schema()
        self.__complete_schema__()       
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
       

    #Introspection of  the models
    def __complete_schema__(self):
        self.lstCampos = []
        if "fields" in self.schema:
            for m in self.schema.get("fields"):
                field_name = m["field_name"]
                setattr(self, field_name, eval(m["class_name"])(**m))
                self.lstCampos.append(field_name)
        if "relationship" in self.schema:  
            for m in self.schema.get("relationship"):
                field_name = m.get("field_name")
                m["parent"] = self
                setattr(self, field_name, eval(m["class_name"])(**m))

    def __cargar_datos__(self, **datos):
        for k, v in datos.items():
            if k=="id":
                self.id = v
            else:
                setattr(self, k, v)
                self.lstCampos.append(k)



    def save(self, **kargs):
        self.__cargar_datos__(**kargs)
        self.id = -1 if self.id == None else self.id

        if self.estado == constant.STATE_NEW:
            keys =[]
            vals = []
            for key in self.lstCampos:
                val = super(Model, self).__getattribute__(key)
                pack_data = val.get_pack_dato()
                if "None" not in pack_data:  
                    keys.append(key)
                    vals.append(pack_data)
            cols = ", ".join(keys)
            values = ", ".join(vals)
            sql = u"INSERT INTO {0} ({1}) VALUES ({2});".format(self.table_name,
                                                                   cols, values)
        else:
            vals = []
            for key in self.lstCampos:
                val = super(Model, self).__getattribute__(key)
                pack_data = val.get_pack_dato()
                if "None" not in pack_data:
                    vals.append(u"{0} = {1}".format(key, pack_data))
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
            if field.dato:
                js[key] = field.get_str_value()
        return js
    
    
    @classmethod
    def filter(cls, *args, **kwargs):
        sql = "SELECT * FROM {0} {1};".format(Utility.default_tb_name(cls), Utility.decode_condition(cls, *args, **kwargs))
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
    def first(cls, *args, **kwargs):
        condition["limit"] = 1
        reg = cls.filter(**kwargs)
        if len(reg) > 0:
            return  reg[0]
            

    @classmethod
    def getByPk(cls, pk):
        sql = u"SELECT * FROM {0} WHERE id={1};".format(Utility.default_tb_name(cls), pk)
        reg, d = Utility.execute_select(sql, Utility.default_db_name(cls))
        if len(reg) > 0:
            reg = reg[0]
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            req_cls = cls()
            req_cls.__cargar_datos__(**res)
            return req_cls
        return None
        

    @classmethod
    def get_schema(cls):
        sql = "SELECT model FROM django_models_db WHERE table_name='%s';" % Utility.default_tb_name(cls)
        reg, c = Utility.execute_select(sql, Utility.default_db_name(cls))
        if reg:
            return json.loads(base64.b64decode(eval(reg[0][0])))
        return None

    
    @classmethod
    def delete_row(cls, **condition):
        sql = "DELETE FROM {0} {1};".format(Utility.default_tb_name(cls), Utility.decode_condition(cls, **condition))
        Utility.execute_query(sql, Utility.default_db_name(cls))

    @classmethod
    def save_schema(cls, schema):
        schema_encode = base64.b64encode(json.dumps(schema).encode())
        sql = u'INSERT OR REPLACE INTO django_models_db (table_name, model) VALUES ("{0}","{1}");'
        sql = sql.format(Utility.default_tb_name(cls), schema_encode)
        Utility.execute_query(sql, Utility.default_db_name(cls))

    @classmethod
    def create_table(cls, campos, fkData):
        fields = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        frgKey = ""
        for key in campos:
            field  = getattr(cls, key)
            fields.append(u"'{0}' {1}".format(key, field.toQuery()))

        if len(fkData["fields"]):
            frgKey = u", {0}".format(", ".join(fkData["fgkeys"]))
            fields = fields + fkData["fields"]
       
        values = ", ".join(fields)
        sql = u"CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            Utility.default_tb_name(cls),
                                                            frgKey)
        Utility.execute_query(sql, Utility.default_db_name(cls))

    @classmethod
    def init_table(cls):
        tb_name = Utility.default_tb_name(cls)
        sql = u"CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT);" % tb_name
        Utility.execute_query(sql, Utility.default_db_name(cls))


    @classmethod
    def alter_constraint(cls, field):
        table_name = Utility.default_tb_name(cls)
        db_name = Utility.default_db_name(cls)
        query = []
        query.append('PRAGMA foreign_keys=off;')
        sql = u" ALTER TABLE {0} ADD COLUMN {1} REFERENCES {2}(id) ON DELETE CASCADE; "
        sql = sql.format(table_name, field.id_field_name, field.othermodel.__name__.lower())
        query.append(sql)
        query.append("PRAGMA foreign_keys=on;")
        Utility.execute_multiple_query(query, db_name)

    @classmethod
    def alter(cls, field):
        table_name = Utility.default_tb_name(cls)
        db_name = Utility.default_db_name(cls)
        query = []
        sql = u"ALTER TABLE {0} ADD COLUMN {1} {2};"
        sql = sql.format(table_name, field.field_name, field.toQuery().replace("NOT NULL", ""))
        query.append(sql)
       
        Utility.execute_multiple_query(query, db_name)

    @classmethod
    def init_model(cls):
        if not Utility.exists_table("django_models_db", Utility.default_db_name(cls)):
            IDprimary = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            sql = "CREATE TABLE IF NOT EXISTS django_models_db (%s, table_name TEXT UNIQUE, model TEXT);"
            sql = sql % IDprimary
            Utility.execute_query(sql, Utility.default_db_name(cls))
        
        #Introspection of the inherited class
        schema = cls.get_schema()
        alter = False
        if not schema:
            schema= {'keys':[], 'fields':[], 'relationship':[]}
            cls.save_schema(schema)
            cls.init_table()
        
        keys = []
        for key in dir(cls):

            field = getattr(cls, key)
            tipo_class = ""
            if hasattr(field, 'tipo_class'):
                tipo_class = field.tipo_class
            if tipo_class == constant.TIPO_CAMPO:
                keys.append(key)
                if key not in schema["keys"]: 
                    schema["keys"].append(key)
                    schema["fields"].append(field.serialize_field(key))
                    cls.alter(field)
                    alter = True
                    
                
            elif tipo_class == constant.TIPO_RELATION:
                keys.append(key)
                if key not in schema["keys"]:
                    alter = True
                    schema["keys"].append(key)
                    serialized_field = field.serialize_field(key)
                    serialized_field["othermodel"] = field.othermodel.__name__

                    othermodel_schema = field.othermodel.get_schema()
                    if not othermodel_schema:
                        raise Exception("Debe llamar a migrate_models con los modelos en orden")
              
                    if field.class_name == "ForeignKey":
                        othermodel_schema["relationship"].append({'othermodel': cls.__name__,
                                                                  'field_name': cls.__name__.lower(),
                                                                  'id_foreignkey': field.id_field_name,
                                                                  'tipo_class': 'tipo_relation',
                                                                  'class_name': 'OneToMany' })
                        cls.alter_constraint(field)
                       
                        schema["fields"].append({"field_name": field.id_field_name, "class_name": 'IntegerField'})
       
                    elif field.class_name == "ManyToManyField":
                        model_nexo = Utility.default_tb_name(field.othermodel)+"_"+Utility.default_db_name(cls)
                        serialized_field["model_nexo"] = model_nexo
                        serialized_field["id_foreignkey"] = cls.__name__.lower()+"_id"
                        serialized_field["ohter_field_name"] = cls.__name__.lower()+"_set"
                        othermodel_schema["relationship"].append({'othermodel': cls.__name__,
                                                                'field_name': cls.__name__.lower()+"_set",
                                                                'other_field_name': field.field_name,
                                                                'id_foreignkey': field.othermodel.__name__.lower() +"_id",
                                                                'tipo_class': 'tipo_relation',
                                                                'model_nexo': model_nexo,
                                                                'class_name': 'ManyToManyField'})
                        Utility.execute_query(field.str_create_tb_nexo(parent=cls), Utility.default_db_name(cls))
                    
                
                    schema["relationship"].append(serialized_field)
                    field.othermodel.save_schema(othermodel_schema)
        

        if alter:
            cls.save_schema(schema)



