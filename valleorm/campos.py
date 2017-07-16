# -*- coding: utf-8 -*-

"""python-ormsqlite Orm simple, potente y versatil

    Autor: Manuel Rodriguez
    Licencia: Apache v2.0

"""
class Campo(object):
    def __init__(self, default=None, tipo="TEXT", dato=None):
        self.dato = dato
        if dato:
            self.tipo = self.__getTipo(dato);
            self.default = dato;
        else:
            self.default = "" if not default else default
            self.tipo = "TEXT" if not tipo else tipo

    def __getTipo(self, dato):
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
            return dato

    def toQuery(self):
        strdefault = "" if not self.default else " DEFAULT %s" % self.pack(self.default)
        return "{0} {1}".format(self.tipo, strdefault)
