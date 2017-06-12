# -*- coding: utf-8 -*-

"""Programa Gestion para el TPV del Btres

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""

class RelationShip(object):

    def __init__(self, tipo, name, parent=None):
        self.tipo = tipo
        self.name = name
        self.parent = parent

    def add(self, child):
        if self.tipo == "MANY":
            setattr(child, "ID"+self.name, self.parent.ID)
            child.save()

    def get(self, condition={}):
        from models import Models
        if self.tipo == "ONE":
            this = Models(tableName=self.name, dbName=self.parent.dbName)
            idParent = getattr(self.parent, "ID"+sel.name)
            this.getPk(idParent)
            return this
        if self.tipo == "MANY":
            this = Models(tableName=self.name, dbName=self.parent.dbName)
            query = ""
            if "query" in condition:
                query = condition.get("query")
                query += " AND {0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            else:
                query = "{0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            condition["query"] = query
            return this.getAll(condition)
        if self.tipo  == "MANYTOMANY":
            this = Models(tableName=self.name, dbName=self.parent.dbName)
            query = ""
            if "query" in condition:
                query = condition.get("query")
                query += " AND {0}={1}".format("ID"+self.name, self.parent.ID)
            else:
                query = "{0}={1}".format("ID"+self.name, self.parent.ID)
            condition["query"] = query
            return this.getAll(condition)
