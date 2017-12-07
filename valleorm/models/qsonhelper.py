# @Author: Manuel Rodriguez <valle>
# @Date:   16-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: controllers.py
# @Last modified by:   valle
# @Last modified time: 06-Sep-2017
# @License: Apache license vesion 2.0

import os
from models import *


class HelperBase(object):
    def __init__(self, JSONQuery, JSONResult):
        self.JSONResult = JSONResult
        self.JSONQuery = JSONQuery
        self.db = JSONQuery.get("db")
        for tb, val in JSONQuery.items():
            if tb == "db":
                pass
            elif type(val) is list:
                rows = val
                for row in rows:
                    keys = row.keys()
                    if len(keys) == 1:
                        self.action(row, keys[0])
                    else:
                        self.action(row, tb)
            else:
                self.action(val, tb)

    def decode_qson(self, qson, tb):
        query = []
        decoder = {"condition":{}, 'tb':tb, 'childs':{"decoders":[]}}
        for col, val in qson.items():
            isWordReserver = col == 'columns' or col == 'limit' or col == 'offset'
            isWordReserver = isWordReserver or col == 'query' or col == 'order'
            isWordReserver = isWordReserver or col == 'joins' or col == 'group'
            if isWordReserver:
                decoder["condition"] = {key: val}
            elif not isWordReserver and type(val) is dict :
                child_decoder = self.decode_qson(val, col)
                decoder['childs']["decoders"].append(child_decoder)
            else:
               packQuery = self.getPackQuery(col, val)
               query.append(packQuery)
        if 'query' in decoder["condition"] and len(query) > 0:
            decoder["condition"]['query'] += " AND "+" AND ".join(query)
        elif len(query) > 0:
            decoder["condition"]['query'] = " AND ".join(query)

        return decoder

    def getPackQuery(self, col, val):
        if type(val) is unicode:
            return col + " LIKE '"+val+"'"
        elif type(val) is float:
            return col + "="+str(val)
        elif type(val) is int:
            return col + "="+str(val)
        else:
            return col + " LIKE '"+val+"'"

class AddHelper(HelperBase):

    def action(self, qson, tb):
        if not 'add' in self.JSONResult:
            self.JSONResult["add"] = {tb:[]}
        decoder = self.decode_qson(qson, tb)
        row = self.modify_row(decoder)
        if row:
            row.save()
            row_send = row.toDICT()
            self.JSONResult["add"][tb].append(row_send)
            for dchild in decoder["childs"]["decoders"]:
                fieldName = decoder["childs"]['fieldName']
                if not fieldName in row_send:
                    row_send[fieldName] = []
                child = self.modify_row(dchild)
                if child:
                    getattr(row, fieldName).add(child)
                    row_send[fieldName].append(child.toDICT())

    def modify_row(self, decoder):
        row = Model(tableName=decoder['tb'], dbName=self.db, model=decoder['model'])
        if 'ID' in decoder["fields"]:
            row.load_by_pk(decoder['fields']['ID'])
            if row.ID == -1: return None
        for key, v in decoder["fields"].items():
            setattr(row, key, v)
        return row

    def decode_qson(self, qson, tb):
        exists_tabla = False
        hasChange = False
        if Model.exitsTable(dbName=self.db, tableName=tb):
            model = Model.getModel(dbName=self.db, tableName=tb)
            exists_tabla = True
        else:
            model = {"fields":[], "relationship": []}

        decoder = {'model':model, 'tb':tb, 'fields': {},
                   'childs': {'fieldName':'', 'decoders':[]}}

        for key, v in qson.items():
            if not type(v) is list and not type(v) is dict:
                if key == "ID":
                    decoder['fields'][key] = v
                else:
                    default, tipo = self.get_tipo(v)
                    decoder['fields'][key] = v
                    field = {
                     'fieldName': key,
                     'fieldDato': default,
                     'fieldTipo': tipo,
                    }
                    if exists_tabla:
                        hasChange = self.compare_and_repare_field(tb, model, field)
                    else:
                        model["fields"].append(field)

            else:
                fieldName = key
                relationName = key
                tipo = "MANY"
                childs = []
                if type(v) is dict:
                    child = v
                    childs = [v]
                elif type(v) is list:
                    child = v[0]
                    childs = v
                    for kr, vr in  child.items():
                        if type(vr) is dict:
                            tipo = "MANYTOMANY"
                            relationName = kr
                            break;
                        else:
                            break;

                rship = {
                    'fieldName': fieldName,
                    'relationName': relationName,
                    'relationTipo': tipo,
                }

                for child in childs:
                    if tipo is "MANYTOMANY":
                        tb = rship['relationName']
                        child = child[tb]
                    subdecoder = self.decode_qson(child, rship["relationName"])
                    decoder["childs"]["fieldName"] = rship["fieldName"]
                    decoder["childs"]["decoders"].append(subdecoder)


                if exists_tabla:
                    hasChange = self.compare_and_repare_ship(model, rship)
                else:
                    model["relationship"].append(rship)


        if hasChange:
            Model.alter_model(dbName=self.db, tableName=tb, model=model)

        return decoder

    def compare_and_repare_field(self, tb, model, field):
        hasChange = False
        key = field['fieldName']
        search = filter(lambda field: field['fieldName'] == key, model['fields'])
        if len(search) <= 0:
            hasChange = True
            model['fields'].append(field)
            Model.alter(dbName=self.db, tableName=tb, field=field)
        return hasChange

    def compare_and_repare_ship(self,  model, qrelation):
        hasChange = False
        key = qrelation['fieldName']
        search = filter(lambda field: field['fieldName'] == key, model['relationship'])
        if len(search) <= 0:
            hasChange = True
            model['relationship'].append(qrelation)

        return hasChange

    def get_tipo(self, val):
        val = self.can_convert(val, op='int')
        val = self.can_convert(val, op='float')
        if type(val) is unicode:
            return ("None", "TEXT")
        elif type(val) is float:
            return (None, "REAL")
        elif type(val) is int:
            return (None, "INTEGER")
        else:
            return ("None", "TEXT")

    def can_convert(self, value, op='int'):
        try:
            if type(value) is unicode:
                if op == 'int':
                    value = int(value)
                if op == 'float' and value.find(".") > 0:
                    value = float(value)
            return value
        except ValueError:
             return value

class GetHelper(HelperBase):
    def action(self, qson, tb):
        if not 'get' in self.JSONResult:
            self.JSONResult["get"] = {tb:[]}
        if not Model.exitsTable(dbName=self.db, tableName=tb):
            return ''
        decoder = self.decode_qson(qson, tb)
        row = Model(tableName=tb, dbName=self.db)
        rows = row.getAll(**decoder['condition'])
        for r in rows:
            row_send = r.toDICT()
            self.JSONResult['get'][tb].append(row_send)
            for dchild in decoder["childs"]["decoders"]:
                childs = getattr(r, dchild['tb']).get(dchild["condition"])
                row_send[dchild['tb']] = Model.toArrayDict(childs)

class RmHelper(HelperBase):
    def action(self, qson, tb):
        if not 'rm' in self.JSONResult:
            self.JSONResult["rm"] = {tb:[]}
        hasChild = False
        if not Model.exitsTable(dbName=self.db, tableName=tb):
            return ''
        decoder = self.decode_qson(qson, tb)
        row = Model(tableName=tb, dbName=self.db)
        rows = row.getAll(**decoder['condition'])
        for r in rows:
            row_send = r.toDICT()
            for dchild in decoder["childs"]["decoders"]:
                childs = getattr(r, dchild['tb']).get(dchild["condition"])
                hasChild = True
                row_send[dchild['tb']] = Model.removeRows(childs)
            if not hasChild:
                row_send = {"ID": r.ID, "remove": "True"}
                r.remove()
                hasChild = False

            self.JSONResult['rm'][tb].append(row_send)

class QSonHelper(object):
    def __init__(self, path="./"):
        self.JSONResult = {}
        self.path = path


    def decode_qson(self, qson):
        for name in qson.keys():
            if "add" == name:
                QSONRequire = qson.get("add")
                if  "db" in QSONRequire:
                    QSONRequire["db"] += "" if ".db" in QSONRequire["db"] else ".db"
                else:
                    raise Exception("No se sabe el nombre de la db desconocido.")
                QSONRequire["db"] = os.path.join(self.path, QSONRequire["db"])
                AddHelper(JSONQuery=QSONRequire, JSONResult=self.JSONResult)

            if "get" == name:
                QSONRequire = qson.get("get")
                if "db" in QSONRequire:
                    QSONRequire["db"] += "" if ".db" in QSONRequire["db"] else ".db"
                else:
                    raise Exception("No se sabe el nombre de la db desconocido.")
                QSONRequire["db"] = os.path.join(self.path, QSONRequire["db"])
                GetHelper(JSONQuery=QSONRequire,
                              JSONResult=self.JSONResult)

            if "rm" == name:
                QSONRequire = qson.get("rm")
                if   "db" in QSONRequire:
                    QSONRequire["db"] += "" if ".db" in QSONRequire["db"] else ".db"
                else:
                    raise Exception("No se sabe el nombre de la db desconocido.")
                QSONRequire["db"] = os.path.join(self.path, QSONRequire["db"])
                RmHelper(JSONQuery=QSONRequire,
                        JSONResult=self.JSONResult)

        return self.JSONResult
