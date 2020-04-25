# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from valleorm.models import *

Model.GLOBAL_DB_NAME = "../db.sqlite3"
class User(Model):
   nombre = Field(default="", tipo="TEXT")
   mail = Field(default="", tipo="TEXT")
   salario = RelationShip(tipo="MANY", name="salario")


class Salario(Model):
   mes = Field(default="", tipo="TEXT")
   salario = Field(default=0.0, tipo="REAL")
   user = RelationShip(tipo="ONE", name="user")


Model.dropDB(Model.GLOBAL_DB_NAME)
user = User(nombre="Manuel Rodriguez", mail="jjjrrisl@ejemoplo.com")
user.save()

sal = Salario(mes = "Mayo", salario = 1500)
user.salario.add(sal)

sal = Salario(mes = "Junio", salario = 1500)
user.salario.add(sal)

sal = Salario(mes = "Julio", salario = 1500)
user.salario.add(sal)

sal = Salario(mes = "Agosto", salario = 1500)
user.salario.add(sal)

#Load data user by ID
user.load_by_pk(1)
print (user.toJSON())
row = user.salario.get()
print(Model.serialize(row))
