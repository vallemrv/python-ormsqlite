# -*- coding: utf-8 -*-

"""python-ormsqlite Orm simple, potente y versatil

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""
class RelationShip(object):

    def __init__(self, tipo, name, parent=None):
        self.tipo = tipo
        self.name = name
        self.parent = parent

    def remove(self, child):
        from models import Models
        if self.tipo == "MANYTOMANY":
            reg = Models(tableName=self.parent.relationName, dbName=self.parent.dbName)
            query = "{0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            query += " AND {0}={1}".format("ID"+child.tableName, child.ID)
            reg.loadByQuery(condition={"query":query})
            reg.remove()

    def add(self, child):
        if self.tipo == "MANY":
            setattr(child, "ID"+self.name, self.parent.ID)
            child.save()
        elif self.tipo == "MANYTOMANY":
            from models import Models
            reg = Models(tableName=self.parent.relationName, dbName=self.parent.dbName)
            setattr(reg, "ID"+self.parent.tableName, self.parent.ID)
            setattr(reg, "ID"+child.tableName, child.ID)
            reg.save()

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
            query = "{0}={1}".format(self.parent.relationName+".ID"+self.parent.tableName, self.parent.ID)
            condition["colunms"] = [self.name+".*"]
            condition["joins"] = [
                {
                  'tableName': self.parent.relationName,
                  'join': self.parent.relationName+".ID"+self.name+"="+self.name+".ID"
                }
            ]
            if "query" in condition:
                query += " AND %s" % condition.get("query")

            condition["query"] = query
            return this.getAll(condition)
