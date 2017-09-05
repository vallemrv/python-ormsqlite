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
import unittest

DB_NAME = "../db.sqlite3"
Model.GLOBAL_DB_NAME = DB_NAME
class DatosTest(unittest.TestCase):

    def runTest(self):
        self.add_user()
        self.add_salarios()
        self.add_puestos()
        self.add_user_puesto()

    def add_user(self):
        user1 = User()
        user1.nombre = "Jose Antonio"
        user1.mail = "joseantoino@test.com"
        user1.save()
        user2 = User()
        user2.nombre = "Antonio luis Fernandez"
        user2.mail = "joseantoino@test.com"
        user2.save()
        self.assertEqual(user1.toDICT(), {u"mail": u"joseantoino@test.com", u"ID": 1, u"nombre": u"Jose Antonio"})
        self.assertEqual(user2.toDICT(), {u"mail": u"joseantoino@test.com", u"ID": 2, u"nombre": u"Antonio luis Fernandez"})

    def add_salarios(self):
        user = User()
        user.load_by_pk(1)
        salario = Salario()
        salario.mes = "Mayo"
        salario.importe = 1500
        salario1 = Salario()
        salario1.mes = "Junio"
        salario1.importe = 1000
        salario2 = Salario()
        salario2.mes = "Julio"
        salario2.importe = 1200
        user.salario.add(salario)
        user.salario.add(salario1)
        user.salario.add(salario2)
        lst = []
        for s in user.salario.get():
            lst.append(s.toDICT())

        self.assertEqual(lst,
        [{u"mes": u"Mayo", u"ID": 1, u"importe": 1500.0, u"IDuser": 1},
        {u"mes": u"Junio", u"ID": 2, "importe": 1000.0, u"IDuser": 1},
        {u"mes": u"Julio", u"ID": 3, "importe": 1200.0, u"IDuser": 1}])

    def add_puestos(self):
        puesto1 = Puesto()
        puesto2 = Puesto()
        puesto1.nombre = "barra"
        puesto1.des = "Servicio de atencion y limpieza de barra"
        puesto1.save()
        puesto2.nombre = "comedor"
        puesto2.des = "Servicio de atencion y limpieza de comedor"
        puesto2.save()
        print Puesto.serialize(puesto1.getAll())

    def add_user_puesto(self):
        puesto = Puesto()
        puesto.load_by_pk(1)
        print puesto.toJSON()
        user = User()
        user.load_by_pk(1)
        print user.toJSON()
        user.puesto.add(puesto)

        puesto.load_by_pk(2)
        print user.toJSON()
        puesto.user.add(user)

if __name__ == '__main__':
    Model.dropDB(DB_NAME)
    DatosTest().runTest()
