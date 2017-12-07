# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 12-Sep-2017
# @License: Apache license vesion 2.0


import inspect
import importlib
from constant import constant

class RelationShip(object):

    def __init__(self, **options):
        self.tipo_class = constant.TIPO_RELATION
        self.related_class = None
        for k, v in options.items():
            setattr(self, k, v)


    def get_id_field_name(self):
        return self.field_name + "_id"

    def get(self, **condition):
        pass

    def get_serialize_data(self, field_name):
        self.field_name = field_name
        lista = self.__dict__
        stado = {}
        for k, v in lista.items():
            if type(v) in (str, int, bool):
                stado[k] = v

        return stado

    id_field_name = property(get_id_field_name)

class OneToMany(RelationShip):
    def __init__(self, othermodel, **kargs):
        super(OneToMany, self).__init__(**kargs)
        self.class_name = "OneToMany"
        self.related_class=None
        if type(othermodel) in (str, unicode):
            self.othermodel = othermodel
        else:
            self.othermodel = othermodel.__name__
            self.related_class = othermodel()

    def get(self, **condition):
        if self.related_class == None:
            self.related_class = create_class_related(self.main_module,
                                                      self.othermodel)

        query = u"{0}={1}".format(self.id_field_name_child,
                                  self.main_model_class.id)
        if 'query' in condition:
            condition['query'] += " AND " + query
        else:
            condition['query'] = query
        return self.related_class.getAll(**condition)


    def add(self, child):
        setattr(child, self.id_field_name_child, self.main_model_class.id)
        child.save()

class ForeignKey(RelationShip):
    def __init__(self, othermodel, on_delete, **kargs):
        super(ForeignKey, self).__init__(**kargs)
        self.class_name = "ForeignKey"
        if type(othermodel) in (str, unicode):
            self.othermodel = othermodel
            self.related_class = create_class_related(self.main_module, self.othermodel)
        else:
            self.othermodel = othermodel.__name__
            self.related_class = othermodel()
        self.main_module = self.related_class.__module__
        self.on_delete = on_delete

    def get_choices(self, **condition):
        return self.related_class.getAll(**condition)

    def get_sql_pk(self):
        name_main_model_class = self.main_model_class.__class__.__name__
        setattr(self, name_main_model_class.lower(), self.related_class)
        rel_many = OneToMany(othermodel=name_main_model_class,
                             field_name=name_main_model_class.lower(),
                             id_field_name_child=self.id_field_name,
                             main_module=self.main_module)

        self.related_class.append_relation(rel_many)
        related_tb = self.related_class.table_name
        sql = u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE"
        sql = sql.format(self.id_field_name, related_tb)

        return sql

    def get(self):
        self.init()
        id_rel = getattr(self.main_model_class, self.id_field_name)
        self.related_class.load_by_pk(pk=id_rel)
        return self.related_class

class ManyToManyField(RelationShip):

    def __init__(self, othermodel, **kargs):
        super(ManyToManyField, self).__init__(**kargs)
        self.class_name = "ManyToManyField"
        self.related_class=None
        if type(othermodel) in (str, unicode):
            self.othermodel = othermodel
        else:
            self.related_class = othermodel()
            self.othermodel = othermodel.__name__

        if self.related_class != None:
            self.main_module = self.related_class.__class__.__module__
        self.tb_nexo_name=None

    def init(self):
        if self.related_class == None:
            self.related_class = create_class_related(self.main_module, self.othermodel)

        self.tb_nexo_name = self.main_model_class.table_name
        self.tb_nexo_name += "_"+self.field_name


    def get_sql_tb_nexo(self):
        othermodel = self.main_model_class.__class__.__name__
        if othermodel != "Model":
            if self.related_class == None or self.tb_nexo_name == None:
                self.init()

            rel = ManyToManyChild(othermodel=self.main_model_class.__class__.__name__,
                                 field_name=self.main_model_class.__class__.__name__.lower(),
                                 primary_relation = False,
                                 tb_nexo_name=self.tb_nexo_name,
                                 main_module=self.main_module)
            self.related_class.append_relation(rel)

            id_nexo = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            frgKey = u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE, "
            frgKey = frgKey.format(self.id_field_name, self.main_model_class.table_name)
            frgKey += u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE"
            frgKey = frgKey.format(rel.id_field_name, self.related_class.table_name)
            sql = u"CREATE TABLE IF NOT EXISTS {0} ({1}, {2} ,{3}, {4});"
            sql = sql.format(self.tb_nexo_name, id_nexo, self.id_field_name+" INTEGER ",
                             rel.id_field_name+" INTEGER ", frgKey)

            return sql


    def get(self, **condition):
        if self.related_class == None or self.tb_nexo_name == None:
            self.init()

        parent_id_field_name = self.main_model_class.table_name+"_id"

        condition["columns"] = [self.related_class.table_name+".*"]

        condition["joins"] = [(self.tb_nexo_name + " ON "+ \
                             self.tb_nexo_name+"."+self.id_field_name+\
                             "="+self.related_class.table_name+".id")]
        query = parent_id_field_name+"="+str(self.main_model_class.id)
        if 'query' in condition:
            condition["query"] += " AND " + query
        else:
            condition["query"] = query

        return self.related_class.getAll(**condition)


    def add(self, *childs):
        from valleorm.django import models
        if self.related_class == None or self.tb_nexo_name == None:
            self.init()

        parent_id_field_name = self.main_model_class.__class__.__name__.lower()+"_id"
        for child in childs:
            child.save()
            nexo = models.Model(table_name=self.tb_nexo_name,
                                dbname=self.main_model_class.dbName,
                                path=self.main_model_class.path)
            nexo.appned_fields([models.IntegerField(field_name=self.id_field_name),
                               models.IntegerField(field_name=parent_id_field_name)])

            query = self.id_field_name+"="+str(child.id)+" AND " +\
                        parent_id_field_name+"="+str(self.main_model_class.id)
            reg_nexo = nexo.getAll(query=query)

            if len(reg_nexo) <= 0:
                setattr(nexo, parent_id_field_name, self.main_model_class.id)
                setattr(nexo, self.id_field_name, child.id)
                nexo.save()


    def delete(self, child):
        from models import Model
        if self.related_class == None or self.tb_nexo_name == None:
            self.init()
        query = u""+self.id_field_name+"="+str(self.main_model_class.id)+" AND " +\
        child.id_field_name+"="+str(child.id)
        nexo = Model(table_name=self.tb_nexo_name, dbname=dbname, path=path,
                     query=query)



class ManyToManyChild(RelationShip):
    def __init__(self, othermodel, **kargs):
        super(ManyToManyChild, self).__init__(**kargs)
        self.class_name = "ManyToManyChild"
        self.othermodel = othermodel


    def get_sql_tb_nexo(self):
        pass


    def get(self, **condition):
        self.related_class = create_class_related(self.main_module, self.othermodel)
        parent_id_field_name = self.main_model_class.table_name+"_id"

        condition["columns"] = [self.related_class.table_name+".*"]

        condition["joins"] = [(self.tb_nexo_name + " ON "+ \
                             self.tb_nexo_name+"."+self.id_field_name+\
                             "="+self.related_class.table_name+".id")]
        query = parent_id_field_name+"="+str(self.main_model_class.id)
        if 'query' in condition:
            condition["query"] += " AND " + query
        else:
            condition["query"] = query


        return self.related_class.getAll(**condition)




class OneToOneField(RelationShip):
    def __init__(self,othermodel, on_delete, parent_link=False,  **kargs):
        super(OneToOneField, self).__init__(**kargs)


def create_class_related(module, class_name):
    modulo = importlib.import_module(module)
    nclass = getattr(modulo,  class_name)
    return nclass()

def create_relation_class(config, parent):
    modulo = importlib.import_module('valleorm.django.models.relatedfields')
    class_name = config.get("class_name")
    nclass = getattr(modulo,  class_name)
    rel_new = nclass(**config)
    rel_new.main_model_class = parent
    return rel_new
