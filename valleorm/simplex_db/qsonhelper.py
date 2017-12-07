# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   16-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: controllers.py
# @Last modified by:   valle
# @Last modified time: 18-Sep-2017
# @License: Apache license vesion 2.0

import os
import importlib
from models import Model
from django.core import serializers
from django.conf import settings

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
                decoder["condition"] = {col: val}
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
            self.JSONResult["add"] = {}

        self.JSONResult["add"][tb] = []
        decoder = self.decode_qson(qson, tb)
        row = self.modify_row(decoder)
        if row:
            row_send = self.execute_decoder(row, decoder, tb)
            self.JSONResult['add'][tb].append(row_send)

    def execute_decoder(self, row, decoder, tb):
        row.save()
        row_send = Model.model_to_dict(row)
        for dchild in decoder["childs"]:
            fieldName = dchild['fieldName']
            if not fieldName in row_send:
                row_send[fieldName] = []
            child = self.modify_row(dchild["decoder"])
            if child:
                db_name = settings.DATABASES["default"]["NAME"]
                Model.add(db_name, self.db, row, child)
                child_row_send = self.execute_decoder(child, dchild["decoder"], fieldName)
                row_send[fieldName].append(child_row_send)
        return row_send




    def modify_row(self, decoder):
        modulo = importlib.import_module(self.db+".models")
        clase_mane = decoder["tb"]
        for s in dir(modulo):
            if s.lower() == decoder["tb"]:
                clase_mane = s
        class_model = getattr(modulo, clase_mane)
        if "condition" in decoder:
            db_name = settings.DATABASES["default"]["NAME"]
            row_id = Model(db_name=db_name, table_name=self.db+"_"+decoder['tb'])
            row_id.load_first_by_query(**decoder["condition"])
            decoder["fields"]["id"] = row_id.id
        if 'id' in decoder["fields"]:
            try:
                row = class_model.objects.get(pk=decoder['fields']['id'])
            except:
                row = class_model()
        else:
            row = class_model()
        for k, v in decoder["fields"].items():
            setattr(row, k, v)
        return row

    def decode_qson(self, qson, tb):
        decoder = {'tb':tb, 'fields': {}, 'childs': []}
        for key, v in qson.items():
            isWordReserver = key == 'query'
            if isWordReserver:
                decoder["condition"]= {key: v}
            elif not isWordReserver and not type(v) is list and not type(v) is dict:
                decoder['fields'][key] = v
            else:
                childs = []
                relationName = key
                if type(v) is dict:
                    childs = [v]
                else:
                    childs = v
                for child in childs:
                    subdecoder = self.decode_qson(child, relationName)
                    dchild = {
                        "fieldName":relationName,
                        "decoder": subdecoder
                    }
                    decoder["childs"].append(dchild)

        return decoder



class GetHelper(HelperBase):
    def __init__(self, JSONQuery, JSONResult):
        self.main_class = JSONQuery.get("db")
        JSONQuery["db"] = settings.DATABASES["default"]["NAME"]
        super(GetHelper, self).__init__(JSONQuery, JSONResult)

    def action(self, qson, tb):
        if not 'get' in self.JSONResult:
            self.JSONResult["get"] = {}
        self.JSONResult["get"][tb] = []
        if not Model.exitsTable(db_name=self.db, table_name=self.main_class+"_"+tb):
            return ''
        decoder = self.decode_qson(qson, tb)
        row = Model(table_name=self.main_class+"_"+tb, db_name=self.db)
        rows = row.getAll(**decoder['condition'])
        list_row_send = self.execute_decoder(rows, decoder, tb)
        self.JSONResult['get'][tb] = list_row_send

    def execute_decoder(self,rows, decoder, tb):
        list_row_send = []
        for r in rows:
            row_send = r.toDICT()
            list_row_send.append(row_send)
            for dchild in decoder["childs"]["decoders"]:
                table_name_child = dchild['tb']
                condition = dchild["condition"]
                childs = Model.get(self.db, self.main_class, r, tb, table_name_child, **condition)
                childs_list_row_send = self.execute_decoder(childs, dchild, table_name_child)
                row_send[dchild['tb']] = childs_list_row_send
        return list_row_send

class RmHelper(HelperBase):
    def __init__(self, JSONQuery, JSONResult):
        self.main_class = JSONQuery.get("db")
        JSONQuery["db"] = settings.DATABASES["default"]["NAME"]
        super(RmHelper, self).__init__(JSONQuery, JSONResult)

    def action(self, qson, tb):
        if not 'rm' in self.JSONResult:
            self.JSONResult["rm"] = {tb:[]}
        if not Model.exitsTable(db_name=self.db, table_name=self.main_class+"_"+tb):
            return ''
        hasChild = False
        decoder = self.decode_qson(qson, tb)
        row = Model(table_name=self.main_class+"_"+tb, db_name=self.db)
        rows = row.getAll(**decoder['condition'])
        for r in rows:
            row_send = r.toDICT()
            for dchild in decoder["childs"]["decoders"]:
                table_name_child = dchild['tb']
                condition = dchild["condition"]
                childs = Model.get(self.db, self.main_class, r, tb, table_name_child, **condition)
                hasChild = True
                row_send[dchild['tb']] = Model.deleteChidls(childs)

            if not hasChild:
                row_send = {"id": r.id}
                r.delete()
                hasChild = False

            self.JSONResult['rm'][tb].append(row_send)

class QSonHelper(object):
    def __init__(self):
        self.JSONResult = {}

    def decode_qson(self, qson):
        for name in qson.keys():
            if "add" == name:
                QSONRequire = qson.get("add")
                AddHelper(JSONQuery=QSONRequire,
                          JSONResult=self.JSONResult)

            if "get" == name:
                QSONRequire = qson.get("get")
                GetHelper(JSONQuery=QSONRequire,
                              JSONResult=self.JSONResult)

            if "rm" == name:
                QSONRequire = qson.get("rm")
                RmHelper(JSONQuery=QSONRequire,
                        JSONResult=self.JSONResult)

        return self.JSONResult
