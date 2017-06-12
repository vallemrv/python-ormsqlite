# -*- coding: utf-8 -*-

"""Programa Gestion para el TPV del Btres

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""

class Campo(object):
    def __init__(self, default=None, tipo=None, dato=None):
        if dato:
            self.tipo = self.__getTipo(dato);
            self.default = dato;
        else:
            self.default = "" if not default else default
            self.tipo = "REAL" if not tipo else tipo

    def __getTipo(self, dato):
        tipo = type(dato)
        if tipo is int:
            return "INTEGER"
        if tipo is float:
            return "REAL"
        else:
            return "TEXT"


    def pack(self, dato):
        if self.tipo is "TEXT":
            return '"{0}"'.format(unicode(dato))
        else:
            return dato

    def toQuery(self):
        return "{0} DEFAULT {1}".format(self.tipo, self.pack(self.default))
