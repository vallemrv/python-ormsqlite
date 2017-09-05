# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: campos.py
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


class Field(object):
    def __init__(self, default=None, tipo="TEXT", dato=None):
        self.dato = dato
        if dato:
            self.tipo = self.__getTipo__(dato);
            self.default = dato;
        else:
            self.default = "" if not default else default
            self.tipo = "TEXT" if not tipo else tipo

    def __getTipo__(self, dato):
        tipo = type(dato)
        if tipo is int:
            return "INTEGER"
        if tipo is float:
            return "REAL"
        else:
            return "TEXT"


    def pack(self, dato):
        if self.tipo == "TEXT" or dato is None:
            return u'\"{0}\"'.format(unicode(dato))
        else:
            return str(dato)

    def toQuery(self):
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "{0} {1}".format(self.tipo, strdefault)
