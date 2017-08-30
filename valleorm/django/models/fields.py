# -*- coding: utf-8 -*-
#
# @Author: Manuel Rodriguez <valle>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: field.py
# @Last modified by:   vallemrv
# @Last modified time: 30-Aug-2017
# @License: Apache license vesion 2.0

import importlib
import uuid
from valleorm.django.models.constant import constant


class Field(object):
    def __init__(self, **options):
        self.tipo_class = constant.TIPO_CAMPO
        self.default = None
        self.null = False
        self.tipo = 'TEXT'
        for k, v in options.items():
            setattr(self, k, v)
        self.dato = self.default

    def get_pack_dato(self):
        if self.tipo == "TEXT" or self.tipo == "VARCHAR" or dato is None:
            return u'\"{0}\"'.format(unicode(self.dato))
        else:
            return self.dato

    def toQuery(self):
        pass

    def get_dato(self):
        return self.dato

    def set_dato(self, value):
        self.dato = value

    def get_serialize_data(self, field_name):
        self.field_name = field_name
        stado = self.__dict__
        return stado

class CharField(Field):
    def __init__(self, max_length, **options):
        super(CharField, self).__init__(**options)
        self.tipo="VARCHAR"
        self.class_name = "CharField"
        self.max_length=max_length


    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "VARCHAR({0}) {1} {2}".format(self.max_length, strnull, strdefault)

class EmailField(CharField):
    def __init__(self, max_length=254, **options):
        super(EmailField, self).__init__(max_length, **options)
        self.class_name = 'EmailField'

class DecimalField(Field):
    def __init__(self, max_digits, decimal_places, **options):
        super(DecimalField, self).__init__(**options)
        self.max_digits=max_digits
        self.decimal_places=decimal_places
        self.class_name = "DecimalField"


    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "DECIMAL({0},{1}) {2} {3}".format(self.max_digits, self.decimal_places,
                                                 strnull, strdefault)

class DateField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, **options):
        super(DateField, self).__init__(**options)
        self.tipo="DATE"
        self.class_name = "DateField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add,



    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "DATE {0} {1}".format(strnull, strdefault)

class DateTimeField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, **options):
        super(DateTimeField, self).__init__(**options)
        self.tipo="DATETIME"
        self.class_name = "DateTimeField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add

    def set_dato(self, value):
        self.dato = value

    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "DATETIME {0} {1}".format(strnull, strdefault)

class BooleanField(Field):
    def __init__(self, **options):
        super(BooleanField, self).__init__(**options)
        self.tipo="BOOL"
        self.class_name = "BooleanField"

    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "BOOL {0} {1}".format(strnull, strdefault)

class IntegerField(Field):
    def __init__(self, **options):
        super(IntegerField, self).__init__(**options)
        self.tipo="INTEGER"
        self.class_name = "IntegerField"

    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "INTEGER {0} {1}".format(strnull, strdefault)

class FloatField(Field):
    def __init__(self, **options):
        super(FloatField, self).__init__(**options)
        self.tipo="REAL"
        self.class_name = "FloatField"

    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "REAL {0} {1}".format(strnull, strdefault)

class TextField(Field):
    def __init__(self, **options):
        super(TextField, self).__init__(**options)
        self.tipo="TEXT"
        self.class_name = "TextField"


    def toQuery(self):
        strnull = 'NOT NULL' if not self.null else 'NULL'
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "TEXT {0} {1}".format(strnull, strdefault)

class UUIDField(Field):
    def __init__(self, **options):
        super(UUIDField, self).__init__(**options)
        self.class_name = "UUIDField"
        self.tipo="TEXT"

    def get_dato(self):
        return str(uuid.uuid4())


    def toQuery(self):
        return "TEXT {0}".format('NOT NULL')



def create_field_class(config):
    modulo = importlib.import_module('valleorm.django.models.fields')
    class_name = config.get("class_name")
    nclass = getattr(modulo,  class_name)
    return nclass(**config)
