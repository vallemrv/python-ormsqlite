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
   puesto = RelationShip(tipo="MANYTOMANY", name="puesto")
   def __init__(self):
       super(User, self).__init__(tableName="user", dbName="valleorm.db" )



class Salario(Models):
   mes = Campo(default="", tipo="TEXT")
   importe = Campo(default=0.0, tipo="REAL")
   user = RelationShip(tipo="ONE", name="user")
   def __init__(self):
       super(Salario, self).__init__(tableName="salario", dbName="valleorm.db" )


class Puesto(Models):
    nombre = Campo(default="", tipo="TEXT")
    des = Campo(default="", tipo="TEXT")
    user = RelationShip(tipo="MANYTOMANY", name="user")
    def __init__(self):
        super(Puesto, self).__init__(tableName="puesto", dbName="valleorm.db" )
