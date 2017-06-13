# orm-python-sqlite

I've done it to work with kivy and android. It works great with mobile devices.
For people who do not seek much complexity.
Just create the model and you can create JSON queries.


:package: Installation
-----------------------

Install it via `pip`

`$ [sudo] pip install valleorm`

Or download zip and then install it by running

`$ [sudo] python setup.py install`

Condition example
-----------------
```javascript
conditionQuery = {
   query: "nombre='Lolo'",
   order: "ID DESC",
   limt: 10,
   offset: 20,
   colunms: ["user.nombre, SUM(salario.salario) AS total"],
   group: "salario.mes"
   joins: [
      {
        typeJoin: "INNER LEFT",
        tableName: "salario",
        join: "ID=IDuser"
      },
      {
         tableName: 'puesto', //for default is INNER JOIN
         join: 'ID=IDuser'
      }
   ]
}

```
```python
some_model = Models()
rows = model.getAll(condition=conditionQuery)
print Models.serialize(rows)

```

Example from Class inheritance Models
-------------------------------------
```python
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

#load data user by ID
user.loadByPk(1)
print user.toJSON()
row = user.salario.get()
print Models.serialize(row)


```

Example from models JSON
------------------------

```python
from valleorm.models import Models

modelUser = {
#Required structure for each relationship 'relationTipo, relationName'
'relationship': [{
    'relationTipo': "MANY", # ACCEPT ONLY  ONE | MANY | MANYTOMANY
    'relationName': "salario", # Table name
}],
#Required structure for each field 'feildName, fieldTipo, fieldDato'
'fields':[
   {
     'fieldName': 'nombre',
     'fieldTipo': 'TEXT', #ACCEPT ONLY TEXT | REAL | INTEGER
     'fieldDato': "", # Value for default
   },
   {
     'fieldName': 'mail',
     'fieldTipo': 'TEXT', #ACCEPT ONLY TEXT | REAL | INTEGER
     'fieldDato': "",
   },
   {
     'fieldName': 'apellido',
     'fieldTipo': 'TEXT', #ACCEPT ONLY TEXT | REAL | INTEGER
     'fieldDato': "",
   }
]}

modelSalario = {
#Required structure for each relationship 'relationTipo, relationName, fieldDato'
'relationship':[{
    'relationTipo': "ONE", # ACCEPT ONLY  ONE | MANY | MANYTOMANY
    'relationName': "user", # Table name
    }],
#Required structure for each field 'feildName, fieldTipo, fieldDato'
'fields':[
   {
     'fieldName': 'mes',
     'fieldTipo': 'TEXT', #ACCEPT ONLY TEXT | REAL | INTEGER
     'fieldDato': "", # Value for default
   },
   {
     'fieldName': 'salario',
     'fieldTipo': 'REAL', #ACCEPT ONLY TEXT | REAL | INTEGER
     'fieldDato': 0.0,
   }
]
}

user = Models(tableName= "user", dbName="valleorm.db", model=modelUser)
sal = Models(tableName= "salario", dbName="valleorm.db", model=modelSalario)

user.mail = "wwwkk@loco.com"
user.nombre = "El loco pitres"
user.apellido = "Fuertes"
user.save()

sal.mes = "may"
sal.salario = "1400"
user.salario.add(sal)
sal = Models(tableName= "salario", dbName="valleorm.db", model=modelSalario)
sal.mes = "jun"
sal.salario = "1400"
user.salario.add(sal)
sal = Models(tableName= "salario", dbName="valleorm.db", model=modelSalario)
sal.mes = "jul"
sal.salario = "1400"
user.salario.add(sal)
sal = Models(tableName= "salario", dbName="valleorm.db", model=modelSalario)
sal.mes = "ago"
sal.salario = "1400"
user.salario.add(sal)

#load data user by ID
user.loadByPk(1)
print user.toJSON()
row = user.salario.get()
print Models.serialize(row)

```

:yum: How to contribute
-----------------------

Have an idea? Found a bug? [add a new issue](https://github.com/vallemrv/orm-python-sqlite/issues) or [fork] (https://github.com/vallemrv/orm-python-sqlite#fork-destination-box) and sendme a pull request. Don't forget to add your name to the Contributors section of this document.

:scroll: License
----------------

Licensed under the Apache-2.0, see `LICENSE`

:heart_eyes: Contributors
--------------------------

Manuel Rodriguez <valle.mrv@gmail.com>
