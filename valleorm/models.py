# -*- coding: utf-8 -*-
"""python-ormsqlite Orm simple, potente y versatil

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""

import sqlite3
import json
import base64
from campos import Campo
from relationship import RelationShip



class Models(object):

    def __init__(self, tableName, dbName, path='./', model=None):
        self.path = path
        self.lstCampos = []
        self.foreingKeys = []
        self.ID = -1
        self.tableName = tableName
        self.dbName = dbName
        self.model = model
        self.columns = "*"
        self.__crea_tb_models__()
        if self.model:
            self.__init_model__()
        elif not type(self) is Models:
            self.__init_campos__()

        if len(self.lstCampos) > 0:
            self.__crearDb__()
        else:
            self.__loadModels__()

    def __crea_tb_models__(self):
        IDprimary = "ID INTEGER PRIMARY KEY AUTOINCREMENT"
        sql = "CREATE TABLE IF NOT EXISTS models_db (%s, table_name TEXT UNIQUE, model TEXT);"
        sql = sql % IDprimary
        self.execute(sql)

    def __save_model__(self, strModel):
        sql = "INSERT OR REPLACE INTO models_db (table_name, model) VALUES ('{0}','{1}');"
        sql = sql.format(self.tableName, strModel)
        self.execute(sql)


    #Introspection of  the models
    def __init_model__(self):
        if len(self.model['fields']) > 0 or len(self.model['relationship']) > 0:
            self.__save_model__(base64.b64encode(json.dumps(self.model)))
        if "fields" in self.model:
            for m in self.model.get("fields"):
                if "fieldName" in m  and "fieldDato" in m and "fieldTipo" in m:
                    setattr(self, "_"+m.get('fieldName'),
                            Campo(default=m.get("fieldDato"), tipo=m.get("fieldTipo")))
                    setattr(self, m.get('fieldName'), m.get("fieldDato"))
                    self.lstCampos.append(m.get("fieldName"))
                else:
                    raise Exception("initModel",
                    'El modelo tiene que contener una extructura concreta. Siga el manual')
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
                        setattr(self, "_"+colRelation, Campo(default= 1, tipo="INTEGER"))
                        setattr(self, colRelation, 1)
                        self.lstCampos.append(colRelation)
                        sql = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                        self.foreingKeys.append(sql.format(colRelation, name))
                    elif m.get("relationTipo") == "MANYTOMANY":
                        self.__crear_tb_nexo__(m.get("relationName"), fieldName)
                else:
                    raise Exception("initModel",
                    'Falta informacion en la relacion. Siga el manual')



    def __find_db_nexo__(self, tb1, tb2):
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        condition = " AND (name='{0}' OR name='{1}')".format(tb1+"_"+tb2, tb2+"_"+tb1)
        sql = "SELECT name FROM sqlite_master WHERE type='table' %s;" % condition
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
            if tipo is Campo:
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
            frgKey = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE, ".format(idnexo1, self.tableName)
            frgKey += "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE".format(idnexo2, relationName)
            sql = "CREATE TABLE IF NOT EXISTS {0} ({1}, {2} ,{3}, {4});".format(nexoName,
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


            sql = "INSERT OR REPLACE INTO models_db (table_name, model) VALUES ('{0}','{1}');"
            sql = sql.format(nexoName, base64.b64encode(json.dumps(nexoModel)))
            self.execute(sql)



    def __crearDb__(self):
        fields = ["ID INTEGER PRIMARY KEY AUTOINCREMENT"]
        for key in self.lstCampos:
            fields.append("{0} {1}".format(key, getattr(self, "_"+key).toQuery()))
        frgKey = "" if len(self.foreingKeys)==0 else ", {0}".format(", ".join(self.foreingKeys))


        values = ", ".join(fields)
        sql = "CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            self.tableName,
                                                            frgKey)
        self.execute(sql)

    def __getenerateJoins__(self, joins):
        strJoins = []
        for j in joins:
            typeJoin = "INNER JOIN " if not "typeJoin" in j else j.get("typeJoin")
            if not "tableName" in j or not "join" in j: raise Exception("joins",
            "La clausulas joins no cumplen con las especificaciones. Consulte el manual")
            sql = "{0} {1} ON {2}".format(typeJoin, j.get("tableName"),  j.get("join"))
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)


    def __loadModels__(self):
        sql = "SELECT model FROM models_db WHERE table_name='%s'" % self.tableName
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            self.model = json.loads(base64.b64decode(reg[0]))
            self.__init_model__()

    def __cargarDatos__(self, datos):
        for k, v in datos.items():
            if k=="ID":
                self.ID = v
            else:
                setattr(self, "_"+k, Campo(dato=v))
                setattr(self, k, v)
                self.lstCampos.append(k)

    def appnedField(self, field):
        self.model["fields"].append(field)
        self.__save_model__(base64.b64encode(json.dumps(self.model)))
        setattr(self, "_"+field.get('fieldName'),
                Campo(default=field.get("fieldDato"), tipo=field.get("fieldTipo")))
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
                    setattr(self, "_"+colRelation, Campo(default= 1, tipo="INTEGER"))
                    setattr(self, colRelation, 1)
                    self.lstCampos.append(colRelation)
                    sql = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                    self.foreingKeys.append(sql.format(colRelation, name))
                elif m.get("relationTipo") == "MANYTOMANY":
                    self.__crear_tb_nexo__(m.get("relationName"), fieldName)

                self.__save_model__(base64.b64encode(json.dumps(self.model)))

    def save(self):
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

                vals.append("{0} = {1}".format(key, _val.pack(val)))
            values = ", ".join(vals)
            sql = u"UPDATE {0}  SET {1} WHERE ID={2};".format(self.tableName,
                                                             values, self.ID);
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        if self.ID == -1:
            self.ID = cursor.lastrowid
        db.commit()
        db.close()

    def remove(self):
        self.ID = -1 if self.ID == None else self.ID
        sql = "DELETE FROM {0} WHERE ID={1};".format(self.tableName,
                                                     self.ID)
        self.execute(sql)
        self.ID = -1

    def vaciar(self):
        self.ID = -1;
        self.execute("DELETE FROM %s;" % self.tableName)

    def loadByQuery  (self, condition={}):
        reg = self.getAll(condition)
        if len(reg) > 0:
            self.__cargarDatos__(reg[0].toDICT())



    def getAll(self, condition={}):
        order = "" if not 'order' in condition else "ORDER BY %s" % unicode(condition.get('order'))
        query = "" if not 'query' in condition else "WHERE %s" % unicode(condition.get("query"))
        limit = "" if not 'limit' in condition else "LIMIT %s" % condition.get("limit")
        offset = "" if not 'offset' in condition else "OFFSET %s" % condition.get('offset')
        self.columns = "*" if not 'columns' in condition else ", ".join(condition.get("columns"))
        joins = "" if not 'joins' in condition else self.__getenerateJoins__(condition.get("joins"))
        group = "" if not 'group' in condition else "GROUP BY %s" % condition.get("group")
        sql = "SELECT {0} FROM {1} {2} {3} {4} {5} {6};".format(self.columns, self.tableName,
                                                         joins, order, query, limit, offset)
        return self.select(sql)

    def select(self, sql):
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        d = cursor.description
        db.commit()
        db.close()
        registros = []

        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = Models(path=self.path, tableName=self.tableName, dbName=self.dbName)
            obj.__cargarDatos__(res)

            registros.append(obj)

        return registros


    def execute(self, query):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(self.path+self.dbName)
            cursor= db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(query)
            db.commit()
            db.close()

    def loadByPk(self, idr):
        sql = "SELECT * FROM {0} WHERE ID={1};".format(self.tableName, idr)
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            self.__cargarDatos__(res)


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
            obj = Models(tableName=l["tableName"], dbName=l["dbName"])
            obj.__cargarDatos__(l["datos"])
            registros.append(obj)

        return registros

    @staticmethod
    def dropDB(dbName, path='./'):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%sqlite%';"
        db = sqlite3.connect(path+dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        for r in reg:
            cursor.execute("DROP TABLE %s" % r)
        db.commit()
        db.close()

    @staticmethod
    def exitsTable(dbName, tableName,  path):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % tableName
        db = sqlite3.connect(path+dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None

    @staticmethod
    def getModel(dbName, tableName, path='./'):
        sql = "SELECT model FROM models_db WHERE table_name='%s'" % tableName
        db = sqlite3.connect(path+dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            return json.loads(base64.b64decode(reg[0]))

    @staticmethod
    def alter(dbName, tableName, field, path='./'):
        sql = "ALTER TABLE {0} ADD COLUMN {1} {2} DEFAULT {3}"
        sql = sql.format(tableName, field["fieldName"], field["fieldTipo"], field["fieldDato"])
        db = sqlite3.connect(path+dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()
