import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm.models import Models
from valleorm.campos import Campo
from valleorm.relationship import RelationShip


class User(Models):
   nombre = Campo(default="", tipo="TEXT")
   mail = Campo(default="", tipo="TEXT")
   salario = RelationShip(tipo="MANY", name="salario")
   def __init__(self):
       super(User, self).__init__(tableName="user", dbName="valleorm.db" )



class Salario(Models):
   mes = Campo(default="", tipo="TEXT")
   salario = Campo(default=0.0, tipo="REAL")
   user = RelationShip(tipo="ONE", name="user")
   def __init__(self):
       super(Salario, self).__init__(tableName="salario", dbName="valleorm.db" )



user = User()
user.nombre = "manolo cara bolo"
user.mail = "jjjrrisl@ejemoplo.com"
user.save()

sal = Salario()
sal.mes = "Mayo"
sal.salario = 1500
user.salario.add(sal)

sal = Salario()
sal.mes = "Junio"
sal.salario = 1500
user.salario.add(sal)

sal = Salario()
sal.mes = "Julio"
sal.salario = 1500
user.salario.add(sal)

sal = Salario()
sal.mes = "Agosto"
sal.salario = 1500
user.salario.add(sal)

#get user by ID
user.getPk(1)
print user.toJSON()
row = user.salario.get()
print Models.serialize(row)
