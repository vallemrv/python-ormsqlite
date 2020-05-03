# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0

import sys
import inspect
import importlib
from . import constant
from .tools import Utility


class __RelationShip__(object):

    def __init__(self, **options):
        self.tipo_class = constant.TIPO_RELATION
        self.parent = None
        self.othermodel = None

        for k, v in options.items():
            setattr(self, k, v)

        


    def get_id_field_name(self):
        return self.field_name+"_id"

    
    def serialize_field(self, field_name):
        self.field_name = field_name
        lista = self.__dict__
        estado = {}
        for k, v in lista.items():
            if type(v) in (str, int, bool):
                estado[k] = v

        return estado

    def fgkey_to_string(self):
        sql = u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE"
        sql = sql.format(self.id_field_name, self.othermodel.__name__.lower())
        return sql
    

    def add(self, child):
        pass

    def get(self):
        return None


    id_field_name = property(get_id_field_name)

class OneToMany(__RelationShip__):
    def __init__(self, othermodel, **kargs):
        super(OneToMany, self).__init__(**kargs)
        self.class_name = "OneToMany"
        if type(othermodel) == str:
            self.othermodel =  getattr(sys.modules["__main__"], othermodel)
         
        
    def get(self, **condition):
        condition["%s__fk" % self.id_foreignkey] = self.parent.id
        return self.othermodel.find(**condition)

    def add(self, child):
        if self.parent != None:
            setattr(child, self.id_foreignkey, self.parent.id)
            child.save()

class ForeignKey(__RelationShip__):
    def __init__(self, othermodel, on_delete, **kargs):
        super(ForeignKey, self).__init__(othermodel=othermodel, **kargs)
        self.class_name = "ForeignKey"
        self.on_delete = on_delete
        if type(othermodel) == str:
            self.othermodel =  getattr(sys.modules["__main__"], othermodel)
       
       

    def get(self):
        return self.othermodel.getByPk(self.parent.id)
    
    
class ManyToManyField(__RelationShip__):

    def __init__(self, othermodel, **kargs):
        super(ManyToManyField, self).__init__(othermodel=othermodel, **kargs)
        self.class_name = "ManyToManyField"
        self.othermodel = othermodel
        if type(othermodel) == str:
            self.othermodel =  getattr(sys.modules["__main__"], othermodel)
        


    def str_create_tb_nexo(self, parent):
        name_other_tb = self.othermodel.__name__ .lower()
        name_parent_tb = parent.__name__.lower() 
        model_nexo = name_other_tb+"_"+name_parent_tb
       
        sql = u"CREATE TABLE IF NOT EXISTS {0} ({1} {2}) ;".format(model_nexo,
                                         "'%s_id' INTEGER NOT NULL, '%s_id' INTEGER NOT NULL, " % (name_other_tb, name_parent_tb),
                                         "FOREIGN KEY({0}_id) REFERENCES {0}(id) ON DELETE CASCADE, FOREIGN KEY({1}_id) REFERENCES {1}(id) ON DELETE CASCADE ".format(
                                         name_other_tb, name_parent_tb))

        return sql

    def get(self, *args, **kwargs):
        kwargs["%s__fk" % self.id_foreignkey] = self.parent.id
        other = self.othermodel()
        column = ", ".join(other.lstCampos)
        other_foreignkey = getattr(other, self.other_field_name).id_foreignkey
        other_tb_name = Utility.default_tb_name(self.othermodel)
        sql = "SELECT {0} FROM {1} INNER JOIN {2} ON {1}.id=={2}.{3} {4}".format(column, other_tb_name, self.model_nexo, other_foreignkey,
        Utility.decode_condition(self.parent, *args, **kwargs))
        reg, d = Utility.execute_select(sql, Utility.default_db_name(self.othermodel))
        registros = []
        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = self.othermodel()
            obj.__cargar_datos__(**res)
            registros.append(obj)

        return registros


    def add(self, child):
        other = getattr(child, self.other_field_name)
        sql = u"INSERT INTO {0} ({1}) VALUES ({2});".format(self.model_nexo,
                                                            "%s, %s" % (other.id_foreignkey, self.id_foreignkey), 
                                                            "%s, %s" % (child.id,self.parent.id))
        Utility.execute_query(sql, Utility.default_db_name(self.othermodel))