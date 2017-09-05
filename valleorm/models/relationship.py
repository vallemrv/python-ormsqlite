# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: relationship.py
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0

class RelationShip(object):

    def __init__(self, tipo, name, fieldName=None, parent=None):
        self.tipo = tipo
        self.name = name
        self.parent = parent
        if fieldName == None:
            self.fieldName = name
        else:
            self.fieldName = fieldName

    def remove(self, child):
        from models import Model
        if self.tipo == "MANY":
            child.remove()
        if self.tipo == "MANYTOMANY":
            reg = Model(tableName=self.parent.relationName, dbName=self.parent.dbName)
            query = "{0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            query += " AND {0}={1}".format("ID"+self.fieldName, child.ID)
            reg.loadByQuery(condition={"query":query})
            reg.remove()

    def add(self, child):
        if self.tipo == "MANY":
            if not hasattr(child, "ID"+self.parent.tableName):
                from models import Model
                child.appendRelations([{
                    'fieldName': self.parent.tableName,
                    'relationName': self.parent.tableName,
                    'relationTipo': 'ONE',
                }])
                Model.alter_constraint(self.parent.dbName, child.tableName,
                                        "ID"+self.parent.tableName,
                                         self.parent.tableName)
            setattr(child, "ID"+self.parent.tableName, self.parent.ID)
            child.save()
        elif self.tipo == "MANYTOMANY":
            from models import Model
            reg = Model(tableName=self.parent.relationName,
                    dbName=self.parent.dbName)
            query = "ID"+self.parent.tableName+'='+str(self.parent.ID)+" AND ID"+self.fieldName+'='+str(child.ID)
            regs = reg.getAll(query = query)
            if child.ID == -1: child.save()
            if len(regs) == 0:
                setattr(reg, "ID"+self.parent.tableName, self.parent.ID)
                setattr(reg, "ID"+self.fieldName, child.ID)
                reg.save()

    def get(self, condition={}):
        from models import Model
        if self.tipo == "ONE":
            this = Model(tableName=self.name, dbName=self.parent.dbName)
            idParent = getattr(self.parent, "ID"+sel.name)
            this.loadByPk(idParent)
            return this
        if self.tipo == "MANY":
            this = Model(tableName=self.name, dbName=self.parent.dbName)
            query = ""
            if "query" in condition:
                query = condition.get("query")
                query += " AND {0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            else:
                query = "{0}={1}".format("ID"+self.parent.tableName, self.parent.ID)
            condition["query"] = query
            return this.getAll(**condition)
        if self.tipo  == "MANYTOMANY":
            this = Model(tableName=self.name, dbName=self.parent.dbName)
            query = "{0}={1}".format(self.parent.relationName+".ID"+
                                     self.parent.tableName, self.parent.ID)
            condition["columns"] = [self.name+".*"] if not 'columns' in condition else condition["columns"]
            condition["joins"] = [
                {
                  'tableName': self.parent.relationName,
                  'join': self.parent.relationName+".ID"+self.fieldName+"="+self.name+".ID"
                }
            ]
            if "query" in condition:
                query += " AND %s" % condition.get("query")

            condition["query"] = query
            return this.getAll(**condition)
