# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm import models

class User(models.Model):
   nombre = models.Field(default="", tipo="TEXT")
   mail = models.Field(default="", tipo="TEXT")
   salario = models.RelationShip(tipo="MANY", name="salario")
   puesto = models.RelationShip(tipo="MANYTOMANY", name="puesto")



class Salario(models.Model):
   mes = models.Field(default="", tipo="TEXT")
   importe = models.Field(default=0.0, tipo="REAL")
   user = models.RelationShip(tipo="ONE", name="user")


class Puesto(models.Model):
    nombre = models.Field(default="", tipo="TEXT")
    des = models.Field(default="", tipo="TEXT")
    user = models.RelationShip(tipo="MANYTOMANY", name="user")
