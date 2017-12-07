# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: models.py
# @Last modified by:   valle
# @Last modified time: 06-Sep-2017
# @License: Apache license vesion 2.0


import sqlite3
import json
import base64

from fields import Field
from relationship import RelationShip

class Model(object):
    GLOBAL_DB_NAME = "db.sqlite3"
    def __init__(self, tableName=None,
                 model=None, dbName=None, **options):
        self.lstCampos = []
        self.foreingKeys = []
        self.ID = -1
        self.columns = "*"
        if tableName == None:
            self.tableName = self.__class__.__name__.lower()
        else:
            self.tableName = tableName
        if dbName == None:
            self.dbName = Model.GLOBAL_DB_NAME
        else:
            self.dbName = dbName
        self.__crea_tb_models__()
        self.model = model

        if self.model == None:
            self.model = Model.getModel(dbName=self.dbName, tableName=self.tableName)

        if self.model != None:
            self.__compare_models__()
            self.__init_model__()
        elif not type(self) is Model:
            self.__init_campos__()

        self.__crearDb__()
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

    def __compare_models__(self):
        guardado = Model.getModel(dbName=self.dbName, tableName=self.tableName)
        hasChange = False
        if guardado == None:
            guardado = {"fields":[], "relationship": []}

        if not "relationship" in self.model:
            hasChange = True
            self.model["relationship"] = []

        if not "relationship" in guardado:
            hasChange = True
            guardado["relationship"] = []

        if len(self.model["fields"]) > len(guardado["fields"]):
            hasChange = True

        if len(self.model["relationship"]) > len(guardado["relationship"]):
            hasChange = True

        if hasChange:
            hasChange = False
            self.__save_model__(base64.b64encode(json.dumps(self.model)))


    def __crea_tb_models__(self):
        IDprimary = "ID INTEGER PRIMARY KEY AUTOINCREMENT"
        sql = "CREATE TABLE IF NOT EXISTS models_db (%s, table_name TEXT UNIQUE, model TEXT);"
        sql = sql % IDprimary
        self.execute(sql)

    def __save_model__(self, strModel):
        sql = u"INSERT OR REPLACE INTO models_db (table_name, model) VALUES ('{0}','{1}');"
        sql = sql.format(self.tableName, strModel)
        self.execute(sql)


    #Introspection of  the models
    def __init_model__(self):
        if "fields" in self.model:
            for m in self.model.get("fields"):
                if "fieldName" in m  and "fieldDato" in m and "fieldTipo" in m:
                    setattr(self, "_"+m.get('fieldName'),
                            Field(default=m.get("fieldDato"), tipo=m.get("fieldTipo")))
                    setattr(self, m.get('fieldName'), m.get("fieldDato"))
                    self.lstCampos.append(m.get("fieldName"))
                else:
                    raise Exception('El modelo tiene que contener una extructura concreta')
        if "relationship" in self.model:
            for m in self.model.get("relationship"):
                if "relationTipo" in m  and "relationName" in  m:
                    fieldName = m.get("fieldName") if 'fieldName' in m else m.get("relationName")
                    setattr(self, fieldName,
                            RelationShip(tipo=m.get("relationTipo"), fieldName=fieldName,
                            name=m.get("relationName"), parent=self))
                    if m.get("relationTipo") == "ONE":
                        colRelation = "ID"+m.get('relationName')
                        name = m.get('relationName')
                        setattr(self, "_"+colRelation, Field(default= 1, tipo="INTEGER"))
                        setattr(self, colRelation, 1)
                        self.lstCampos.append(colRelation)
                        sql = u"FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                        self.foreingKeys.append(sql.format(colRelation, name))
                    elif m.get("relationTipo") == "MANYTOMANY":
                        self.__crear_tb_nexo__(m.get("relationName"), fieldName)
                else:
                    raise Exception('Falta informacion en la relacion')



    def __find_db_nexo__(self, tb1, tb2):
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        condition = u" AND (name='{0}' OR name='{1}')".format(tb1+"_"+tb2, tb2+"_"+tb1)
        sql = u"SELECT name FROM sqlite_master WHERE type='table' %s;" % condition
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        find = False
        if reg:
            find = True
            self.relationName = reg[0]
        return find


    #Introspection of the inherited class
    def __init_campos__(self):
        self.model = {'fields':[],'relationship':[]}
        for key in dir(self):
            tipo = type(getattr(self, key))
            if tipo is Field:
                campo = getattr(self, key)
                self.model["fields"].append(
                            {"fieldName":key,
                             "fieldTipo":campo.tipo,
                             "fieldDato": campo.default
                             })
            elif tipo is RelationShip:
                relationship = getattr(self, key)
                self.model["relationship"].append(
                            {"relationTipo":relationship.tipo,
                             "relationName":relationship.name,
                             "fieldName": key
                             })
        self.__init_model__()

    def __crear_tb_nexo__(self, relationName, fieldName):
        if not self.__find_db_nexo__(self.tableName, relationName):
            nexoName = self.tableName+"_"+fieldName
            self.relationName = nexoName
            idnexo1 = "ID"+self.tableName
            idnexo2 = "ID"+fieldName

            IDprimary = "ID INTEGER PRIMARY KEY AUTOINCREMENT"
            frgKey = u"FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE, ".format(idnexo1, self.tableName)
            frgKey += u"FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE".format(idnexo2, relationName)
            sql = u"CREATE TABLE IF NOT EXISTS {0} ({1}, {2} ,{3}, {4});".format(nexoName,
                                                                IDprimary, idnexo1+" INTEGER ",
                                                                idnexo2+" INTEGER ", frgKey)
            self.execute(sql)
            nexoModel = {
            'fields':[{
                "fieldName":  idnexo1,
                 "fieldTipo": "INTEGER",
                 "fieldDato": 1
                },
                {
                "fieldName":  idnexo2,
                 "fieldTipo": "INTEGER",
                 "fieldDato": 1
                },
                ]}


            sql = u"INSERT OR REPLACE INTO models_db (table_name, model) VALUES ('{0}','{1}');"
            sql = sql.format(nexoName, base64.b64encode(json.dumps(nexoModel)))
            self.execute(sql)



    def __crearDb__(self):
        fields = ["ID INTEGER PRIMARY KEY AUTOINCREMENT"]
        for key in self.lstCampos:
            fields.append(u"{0} {1}".format(key, getattr(self, "_"+key).toQuery()))
        frgKey = "" if len(self.foreingKeys)==0 else u", {0}".format(", ".join(self.foreingKeys))


        values = ", ".join(fields)
        sql = u"CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            self.tableName,
                                                            frgKey)
        self.execute(sql)

    def __getenerate_joins__(self, joins):
        strJoins = []
        for j in joins:
            sql = j if j.startswith("INNER") else "INNER JOIN "+j
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)


    def __loadModels__(self):
        sql = "SELECT model FROM models_db WHERE table_name='%s'" % self.tableName
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            self.model = json.loads(base64.b64decode(reg[0]))
            self.__init_model__()

    def __cargarDatos__(self, **datos):
        for k, v in datos.items():
            if k=="ID":
                self.ID = v
            else:
                setattr(self, "_"+k, Field(dato=v))
                setattr(self, k, v)
                self.lstCampos.append(k)

    def appnedField(self, field):
        self.model["fields"].append(field)
        self.__save_model__(base64.b64encode(json.dumps(self.model)))
        setattr(self, "_"+field.get('fieldName'),
                Field(default=field.get("fieldDato"), tipo=field.get("fieldTipo")))
        setattr(self, field.get('fieldName'), field.get("fieldDato"))
        self.lstCampos.append(field.get("fieldName"))

    def appendRelations(self, relations):
        relationship = self.model["relationship"]
        for m in relations:
            key = m["relationName"]
            search = filter(lambda rel: rel['relationName'] == key, relationship)
            if len(search) <= 0:
                self.model["relationship"].append(m)
                fieldName = m.get("fieldName") if 'fieldName' in m else m.get("relationName")
                setattr(self, fieldName,
                        RelationShip(tipo=m.get("relationTipo"), fieldName=fieldName,
                            name=m.get("relationName"), parent=self))
                if m.get("relationTipo") == "ONE":
                    colRelation = "ID"+m.get('relationName')
                    name = m.get('relationName')
                    setattr(self, "_"+colRelation, Field(default= 1, tipo="INTEGER"))
                    setattr(self, colRelation, 1)
                    self.lstCampos.append(colRelation)
                    sql = u"FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                    self.foreingKeys.append(sql.format(colRelation, name))
                elif m.get("relationTipo") == "MANYTOMANY":
                    self.__crear_tb_nexo__(m.get("relationName"), fieldName)

                self.__save_model__(base64.b64encode(json.dumps(self.model)))

    def save(self, **condition):
        self.__cargarDatos__(**condition)
        self.ID = -1 if self.ID == None else self.ID
        if self.ID == -1:
            keys =[]
            vals = []
            for key in self.lstCampos:
                _val = getattr(self, "_"+key)
                val = getattr(self, key)
                keys.append(key)
                vals.append(unicode(_val.pack(val)))
            cols = ", ".join(keys)
            values = ", ".join(vals)
            sql = u"INSERT INTO {0} ({1}) VALUES ({2});".format(self.tableName,
                                                               cols, values);
        else:
            vals = []
            for key in self.lstCampos:
                _val = getattr(self, "_"+key)
                val = getattr(self, key)

                vals.append(u"{0} = {1}".format(key, unicode(_val.pack(val))))
            values = ", ".join(vals)
            sql = u"UPDATE {0}  SET {1} WHERE ID={2};".format(self.tableName,
                                                             values, self.ID);
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        if self.ID == -1:
            self.ID = cursor.lastrowid
        db.commit()
        db.close()

    def remove(self):
        self.ID = -1 if self.ID == None else self.ID
        sql = u"DELETE FROM {0} WHERE ID={1};".format(self.tableName,
                                                     self.ID)
        self.execute(sql)
        self.ID = -1

    def vaciar(self):
        self.ID = -1;
        self.execute("DELETE FROM %s;" % self.tableName)

    def load_first_by_query(self, **condition):
        reg = self.getAll(condition)
        if len(reg) > 0:
            self.__cargarDatos__(**reg[0].toDICT())



    def getAll(self, **condition):
        order = "" if not 'order' in condition else "ORDER BY %s" % unicode(condition.get('order'))
        query = "" if not 'query' in condition else "WHERE %s" % unicode(condition.get("query"))
        limit = "" if not 'limit' in condition else "LIMIT %s" % condition.get("limit")
        offset = "" if not 'offset' in condition else "OFFSET %s" % condition.get('offset')
        self.columns = "*" if not 'columns' in condition else ", ".join(condition.get("columns"))
        joins = "" if not 'joins' in condition else self.__getenerate_joins__(condition.get("joins"))
        group = "" if not 'group' in condition else "GROUP BY %s" % condition.get("group")
        sql = u"SELECT {0} FROM {1} {2} {3} {4} {5} {6} {7};".format(self.columns, self.tableName,
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
            obj = Model(tableName=self.tableName, dbName=self.dbName)
            obj.__cargarDatos__(**res)
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

    def load_by_pk(self, pk):
        sql = u"SELECT * FROM {0} WHERE ID={1};".format(self.tableName, pk)
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            self.__cargarDatos__(**res)


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

    @staticmethod
    def toArrayDict(registros):
        lista = []
        for r in registros:
            reg = r.toDICT()
            lista.append(reg)

        return lista

    @staticmethod
    def removeRows(registros):
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
            reg["tableName"] = r.tableName
            reg["dbName"] = r.dbName
            reg["datos"] = r.toDICT()
            lista.append(reg)

        return json.dumps(lista)



    @staticmethod
    def deSerialize(dbJSON):
        lista = json.loads(dbJSON)
        registros = []
        for l in lista:
            obj = Model(tableName=l["tableName"], dbName=l["dbName"])
            obj.__cargarDatos__(**l["datos"])
            registros.append(obj)

        return registros

    @staticmethod
    def dropDB(dbName):
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
    def exitsTable(dbName, tableName):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % tableName
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None

    @staticmethod
    def getModel(dbName, tableName):
        sql = "SELECT model FROM models_db WHERE table_name='%s'" % tableName
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            return json.loads(base64.b64decode(reg[0]))

    @staticmethod
    def alter_model(dbName, tableName):
        strModel = base64.b64encode(json.dumps(model))
        sql = u"INSERT OR REPLACE INTO models_db (table_name, model) VALUES ('{0}','{1}');"
        sql = sql.format(tableName, strModel)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        #cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter_constraint(dbName, tableName, columName, parent):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} INTEGER REFERENCES {2}(ID) ON DELETE CASCADE;"
        sql = sql.format(tableName, columName, parent)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter(dbName, tableName, field):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} {2} DEFAULT {3};"
        sql = sql.format(tableName, field["fieldName"], field["fieldTipo"], field["fieldDato"])
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()
