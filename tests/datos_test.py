import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from modelo_heredado import User, Salario, Puesto
def crear_users():
    user1 = User()
    user1.nombre = "Jose Antonio"
    user1.mail = "joseantoino@test.com"
    user1.save()
    user2 = User()
    user2.nombre = "Antonio luis Fernandez"
    user2.mail = "joseantoino@test.com"
    user2.save()
    sal = Salario()
    sal.mes = "Mayo"
    sal.importe = "1500"
    user1.salario.add(sal)
    user2.salario.add(sal)
    print User.serialize(user1.getAll())

def crear_puestos():
    puesto1 = Puesto()
    puesto2 = Puesto()
    puesto1.nombre = "barra"
    puesto1.des = "Servicio de atencion y limpieza de barra"
    puesto1.save()
    puesto2.nombre = "comedor"
    puesto2.des = "Servicio de atencion y limpieza de comedor"
    puesto2.save()
    print Puesto.serialize(puesto1.getAll())


def add_user_puesto():
    puesto = Puesto()
    puesto.getPk(1)
    print puesto.toJSON()
    user = User()
    user.getPk(1)
    print user.toJSON()
    user.puesto.add(puesto)

    user.getPk(2)
    print user.toJSON()
    puesto.user.add(user)

#crear_users()
#crear_puestos()
user = User()
user.getPk(1)
print user.toJSON()
puestos = user.puesto.get()
for p in puestos:
    print p.toJSON()





import unittest

class TestDatos(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
