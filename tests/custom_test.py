# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelo_heredado import User, Salario, Puesto
from valleorm.models import Model

Model.GLOBAL_DB_NAME = "../db.sqlite3"
def test_foreingkey():
    print ("Todos los salarios con su usuarios")
    print (Salario.serialize(Salario().getAll()))

    user = User()
    print ("Todos los usuarios")
    print (User.serialize(User().getAll()))
    user.vaciar()
    print ("Usuarios despues de vaciar no puede haber")
    print (User.serialize(User().getAll()))
    print ("Salarios despues de vaciar usuarios no puede haber")
    print (Salario.serialize(Salario().getAll()))

def test_schema():
    user = Model(tableName="user")
    user.load_by_pk(1)
    puestos = user.puesto.get()
    print( Puesto.serialize(puestos))


if __name__ == '__main__':
    for u in User().getAll():
        print(u.nombre)
