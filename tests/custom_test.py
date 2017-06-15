import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from valleorm.models import Models
from modelo_heredado import User, Salario, Puesto

def test_foreingkey():
    print "Todos los salarios con su usuarios"
    print Salario.serialize(Salario().getAll())

    user = User()
    print "Todos los usuarios"
    print User.serialize(User().getAll())
    user.vaciar()
    print "Usuarios despues de vaciar no puede haber"
    print User.serialize(User().getAll())
    print "Salarios despues de vaciar usuarios no puede haber"
    print Salario.serialize(Salario().getAll())

def test_schema():
    user = Models(tableName="user", dbName="valleorm.db")
    user.loadByPk(1)
    puestos = user.puesto.get()
    print Puesto.serialize(puestos)


if __name__ == '__main__':
    test_schema()
