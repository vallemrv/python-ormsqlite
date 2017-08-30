# coding: utf8
#
# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   vallemrv
# @Last modified time: 30-Aug-2017
# @License: Apache license vesion 2.0


import inspect
import importlib
from valleorm.django.models.constant import constant

class RelationShip(object):

    def __init__(self, **options):
        self.tipo_class = constant.TIPO_RELATION
        for k, v in options.items():
            setattr(self, k, v)

    def get(self, **condition):
        pass


    def get_serialize_data(self, field_name):
        self.field_name = field_name
        stado = self.__dict__
        return stado

class ManyToOne(RelationShip):
    def __init__(self, othermodel, **kargs):
        super(ManyToOne, self).__init__(**kargs)
        self.class_name = "ManyToOne"
        self.othermodel = othermodel

    def get(self, **condition):
        related_class = create_class_related(self.othermodel)
        id_rel = getattr(self.class_parent, "ID"+self.field_name)
        return self.related_class.getAll(query={"ID="+id_rel})




class ForeignKey(RelationShip):
    def __init__(self, othermodel, on_delete, **kargs):
        super(ForeignKey, self).__init__(**kargs)
        self.class_name = "ForeignKey"
        self.othermodel = othermodel
        self.on_delete = on_delete

    def get_choices(self, **condition):
        pass

    def get_sql_pk(self):
        module = inspect.getmodule(inspect.currentframe().f_back)
        self.related_class = create_class_related(module, self.othermodel)
        rel_many = ManyToOne(othermodel=self.parent.__name__)
        self.related_class.append_relation(rel_many)
        related_tb = self.related_class.table_name
        return u"FOREIGN KEY({0}) REFERENCES {1}(ID) ON DELETE CASCADE".format(self.field_name, related_tb)

    def get(self):
        id_rel = getattr(self.class_parent, "ID"+self.field_name)
        return self.related_class.getAll(query={"ID="+id_rel})



class ManyToMany(RelationShip):
    def __init__(self, othermodel, **kargs):
        super(ManyToMany, self).__init__(**kargs)

class OneToOneField(RelationShip):
    def __init__(self,othermodel, on_delete, parent_link=False,  **kargs):
        super(OneToOneField, self).__init__(**kargs)


def create_class_related(module, class_name):
    modulo = importlib.import_module(module.__name__)
    nclass = getattr(modulo,  class_name)
    return nclass()

def create_relation_class(config, parent):
    modulo = importlib.import_module('valleorm.django.models.relatedfields')
    class_name = config.get("class_name")
    nclass = getattr(modulo,  class_name)
    rel_new = nclass(**config)
    rel_new.parent = parent
    return rel_new
