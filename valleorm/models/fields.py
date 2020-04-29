# -*- coding: utf-8 -*-
#
# @Author: Manuel Rodriguez <valle>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: field.py
# @Last modified by:   valle
# @Last modified time: 03-Sep-2017
# @License: Apache license vesion 2.0

import importlib
import uuid
from builtins import ValueError
from . import constant
from decimal import *
from datetime import date, datetime



class __Field__(object):
    def __init__(self, **options):
        self.tipo_class = constant.TIPO_CAMPO
        self.default = None
        self.null = False
        self.tipo = 'TEXT'
        for k, v in options.items():
            setattr(self, k, v)
        self.dato = self.default

    def get_pack_dato(self):
        if self.tipo in ["TEXT", "VARCHAR", "DATE", "DATETIME"]:
            return u'"{0}"'.format(self.get_dato())
        else:
            return str(self.get_dato())

    def get_dato(self):
        if self.dato == None and self.default != None:
            self.dato = self.default
        elif self.null == False and self.dato == None:
            raise ValueError("Error el valor no puede ser nulo")
        return self.dato

    def set_dato(self, value):
        self.dato = value

   
    def get_serialize_data(self, field_name):
        self.field_name = field_name
        estado = self.__dict__
        return estado

    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.get_pack_dato(self.default)
        return u"{2} {0} {1}".format(strnull, strdefault, self.tipo)

    def get_str_value(self):
        return str(self.get_dato())



class TextField(__Field__):
    pass

class CharField(__Field__):
    def __init__(self, max_length, **options):
        super(CharField, self).__init__(**options)
        self.tipo="VARCHAR"
        self.class_name = "CharField"
        self.max_length=max_length


    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.get_pack_dato(self.default)
        return "VARCHAR({0}) {1} {2}".format(self.max_length, strnull, strdefault)

class EmailField(CharField):
    def __init__(self, max_length=254, **options):
        super(EmailField, self).__init__(max_length, **options)
        self.class_name = 'EmailField'

    def set_dato(self, value):
        if not ("@" in value and "." in value):
            raise ValueError('Formato email no valido')
        self.dato = value


class DecimalField(__Field__):
    def __init__(self, max_digits, decimal_places, **options):
        super(DecimalField, self).__init__(**options)
        self.max_digits=max_digits
        self.decimal_places=decimal_places
        self.class_name = "DecimalField"
        self.tipo = "NUMERIC"

    def set_dato(self, value):
        if value != None and type(value) == str and value.strip() != "":
            self.dato = float(value.replace(",", "."))
        else:
            self.dato = value
        format = "%0.{0}f".format(self.decimal_places)
        self.dato = Decimal(format % self.dato)
        
    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.get_pack_default()
        return u"DECIMAL({0},{1}) {2} {3}".format(self.max_digits, self.decimal_places,
                                                 strnull, strdefault)

class DateField(__Field__):
    def __init__(self, auto_now=False, auto_now_add=True, **options):
        super(DateField, self).__init__(**options)
        self.tipo="DATE"
        self.class_name = "DateField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add

    def set_dato(self, value):
        if value is str:
            self.dato = datetime.strptime(value, '%m/%d/%y')
        else:
            self.dato = value

    def get_dato(self):
        if self.auto_now:
            self.dato = datetime.now()
        elif self.auto_now_add and self.dato == None:
            self.dato = datetime.now()
        elif self.null == False and self.dato == None:
            raise ValueError("El dato no puede ser null")

        return self.dato


    def get_pack_dato(self):
        return u'"{0}"'.format(self.get_dato().strftime('%m/%d/%y'))

    def get_str_value(self):
        return self.get_dato().strftime('%m/%d/%y')



class DateTimeField(__Field__):
    def __init__(self, auto_now=False, auto_now_add=False, **options):
        super(DateTimeField, self).__init__(**options)
        self.tipo="DATETIME"
        self.class_name = "DateTimeField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add

    def set_dato(self, value):
        if value is str:
            self.dato = datetime.strptime(value, '%m/%d/%y %H:%M:%S')
        else:
            self.dato = value

    def get_dato(self):
        if self.auto_now:
            self.dato = datetime.now()
        elif self.auto_now_add and self.dato == None:
            self.dato = datetime.now()
        elif self.null == False and self.dato == None:
            raise ValueError("El dato no puede ser null")

        return self.dato


    def get_pack_dato(self):
        return u'"{0}"'.format(self.get_dato().strftime('%m/%d/%y %H:%M:%S'))

    def get_str_value(self):
        return self.get_dato().strftime('%m/%d/%y %H:%M:%S')


class BooleanField(__Field__):
    def __init__(self, **options):
        super(BooleanField, self).__init__(**options)
        self.tipo="BOOL"
        self.class_name = "BooleanField"

    def set_dato(self, value):
        if value:
            self.dato = True
        else:
            self.dato = False

    def get_pack_dato(self):
        return "1" if self.get_dato() else "0"

class IntegerField(__Field__):
    def __init__(self, **options):
        super(IntegerField, self).__init__(**options)
        self.tipo="INTEGER"
        self.class_name = "IntegerField"


class FloatField(__Field__):
    def __init__(self, **options):
        super(FloatField, self).__init__(**options)
        self.tipo="REAL"
        self.class_name = "FloatField"


class TextField(__Field__):
    def __init__(self, **options):
        super(TextField, self).__init__(**options)
        self.tipo="TEXT"
        self.class_name = "TextField"


class UUIDField(__Field__):
    def __init__(self, **options):
        super(UUIDField, self).__init__(**options)
        self.class_name = "UUIDField"
        self.tipo="TEXT"

    def get_dato(self):
        return str(uuid.uuid4())


    def toQuery(self):
        return "TEXT {0}".format('NOT NULL')


def create_field_class(config):
    modulo = importlib.import_module('valleorm.models.fields')
    class_name = config.get("class_name")
    nclass = getattr(modulo,  class_name)
    return nclass(**config)
