# -*- coding: utf-8 -*-
"""Programa Gestion para el TPV del Btres

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""

import sqlite3
import json
from campos import Campo
from relationship import RelationShip



class Models(object):

    def __init__(self, tableName, dbName, model=None):
        self.path = "./"
        self.lstCampos = []
        self.foreingKeys = []
        self.ID = -1
        self.tableName = tableName
        self.dbName = dbName
        self.model = model
        if self.model:
            self.__init_model__()
        else:
            self.__init_campos__()
        if len(self.lstCampos) > 0:
            self.__crearDb__()

    #Introspection of  the models
    def __init_model__(self):
        if self.model:
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
                        setattr(self, m.get('relationName'),
                                RelationShip(tipo=m.get("relationTipo"), name=m.get("relationName"), parent=self))
                        if m.get("relationTipo") == "ONE":
                            colRelation = "ID"+m.get('relationName')
                            name = m.get('relationName')
                            setattr(self, "_"+colRelation, Campo(default= 1, tipo="INTEGER"))
                            setattr(self, colRelation, 1)
                            self.lstCampos.append(colRelation)
                            sql = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                            self.foreingKeys.append(sql.format(colRelation, name))
                        elif m.get("relationTipo") == "MANYTOMANY":
                            self.__crear_tb_nexo__(m.get("relationName"))
                    else:
                        raise Exception("initModel",
                        'Falta informacion en la relacion. Siga el manual')



    def __find_db_nexo__(self, tb1, tb2):
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        condition = " AND (name='{0}' OR name='{1}')".format(tb1+"_"+tb2, tb2+"_"+tb1)
        sql = "SELECT name FROM sqlite_master WHERE type='table' %s;" % condition
        cursor.execute(sql)
        reg = cursor.fetchall()
        db.commit()
        db.close()
        find = False
        if len(reg) > 0:
            find = True
            self.relationName = reg[0][0]
        return find


    #Introspection of the inherited class
    def __init_campos__(self):
        for key in dir(self):
            tipo = type(getattr(self, key))
            if tipo is Campo:
                campo = getattr(self, key)
                setattr(self, "_"+key, Campo(default=campo.default, tipo=campo.tipo))
                setattr(self, key, campo.default)
                self.lstCampos.append(key)
            elif tipo is RelationShip:
                relationship = getattr(self, key)
                setattr(self, key, RelationShip(tipo=relationship.tipo,
                                                name=relationship.name,
                                                parent=self))
                if relationship.tipo == "ONE":
                    colRelation = "ID"+relationship.name
                    setattr(self, "_"+colRelation, Campo(dato=1, tipo="INTEGER"))
                    setattr(self, colRelation, 1)
                    self.lstCampos.append(colRelation)
                    sql = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE"
                    self.foreingKeys.append(sql.format(colRelation, self.tableName))
                elif relationship.tipo == "MANYTOMANY":
                    self.__crear_tb_nexo__(relationship.name)


    def __crear_tb_nexo__(self, relationName):
        if not self.__find_db_nexo__(self.tableName, relationName):
            nexoName = self.tableName+"_"+relationName
            idnexo1 = "ID"+self.tableName
            idnexo2 = "ID"+relationName

            IDprimary = "ID INTEGER PRIMARY KEY AUTOINCREMENT"
            frgKey = "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE, ".format(idnexo1, self.tableName)
            frgKey += "FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE".format(idnexo2, relationName)
            sql = "CREATE TABLE IF NOT EXISTS {0} ({1}, {2} ,{3}, {4});".format(nexoName,
                                                                IDprimary, idnexo1+" INTEGER ",
                                                                idnexo2+" INTEGER ", frgKey)
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

    def loadSchema(self):
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        sql = "PRAGMA table_info(%s);" % self.tableName
        cursor.execute(sql)
        reg = cursor.fetchall()
        db.commit()
        db.close()
        datos = {}
        for d in reg:
            datos[d[1]] = d[4]
        self.__cargarDatos(datos)


    def save(self):
        if self.ID == -1 or self.ID == None:
            keys =[]
            vals = []
            for key in self.lstCampos:
                _val = getattr(self, "_"+key)
                val = getattr(self, key)
                keys.append(key)
                vals.append(str(_val.pack(val)))
            cols = ", ".join(keys)
            values = ", ".join(vals)
            sql = "INSERT INTO {0} ({1}) VALUES ({2});".format(self.tableName,
                                                               cols, values);
        else:
            vals = []
            for key in self.lstCampos:
                _val = getattr(self, "_"+key)
                val = getattr(self, key)
                vals.append("{0} = {1}".format(key, _val.pack(val)))
            values = ", ".join(vals)
            sql = "UPDATE {0}  SET {1} WHERE ID={2};".format(self.tableName,
                                                             values, self.ID);
        db = sqlite3.connect(self.path+self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        if self.ID == -1:
            self.ID = cursor.lastrowid
        db.commit()
        db.close()

    def remove(self):
        sql = "DELETE FROM {0} WHERE ID={1};".format(self.tableName,
                                                     self.ID)
        self.execute(sql)
        self.ID = -1

    def __getenerateJoins(self, joins):
        strJoins = []
        for j in joins:
            typeJoin = "INNER JOIN " if not "typeJoin" in j else j.get("typeJoin")
            if not "tableName" in j or not "join" in j: raise Exception("joins",
            "La clausulas joins no cumplen con las especificaciones. Consulte el manual")
            sql = "{0} {1} ON {2}".format(typeJoin, j.get("tableName"),  j.get("join"))
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)

    def getAll(self, condition={}):
        order = "" if not 'order' in condition else "ORDER BY %s" % unicode(condition.get('order'))
        query = "" if not 'query' in condition else "WHERE %s" % unicode(condition.get("query"))
        limit = "" if not 'limit' in condition else "LIMIT %s" % condition.get("limit")
        offset = "" if not 'offset' in condition else "OFFSET %s" % condition.get('offset')
        colunms = "*" if not 'colunms' in condition else ", ".join(condition.get("colunms"))
        joins = "" if not 'joins' in condition else self.__getenerateJoins(condition.get("joins"))
        group = "" if not 'group' in condition else "GROUP BY %s" % condition.get("group")
        sql = "SELECT {0} FROM {1} {2} {3} {4} {5} {6};".format(colunms, self.tableName,
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
            obj = Models(tableName=self.tableName, dbName=self.dbName)
            obj.__cargarDatos(res)

            registros.append(obj)

        return registros


    def execute(self, query):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(self.path+self.dbName)
            cursor= db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()

    def getPk(self, idr):
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
            self.__cargarDatos(res)


    def toJSON(self):
        js = {"ID": self.ID}
        for key in self.lstCampos:
            js[key] = getattr(self, key)

        return json.dumps(js)

    def toDICT(self):
        js = {"ID": self.ID}
        for key in self.lstCampos:
            js[key] = getattr(self, key)

        return js

    def __cargarDatos(self, datos):
        for k, v in datos.items():
            if k=="ID":
                self.ID = v
            else:
                setattr(self, "_"+k, Campo(dato=v))
                setattr(self, k, v)
                self.lstCampos.append(k)


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
    def deSerialize(cls, dbJSON):
        lista = json.loads(dbJSON)
        registros = []
        for l in lista:
            obj = Models(tableName=l["tableName"], dbName=l["dbName"])
            obj.__cargarDatos(l["datos"])
            registros.append(obj)

        return registros
