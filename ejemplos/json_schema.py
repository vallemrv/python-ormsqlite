# -*- coding: utf-8 -*-
# allow direct execution
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
     'fieldDato': '0.0',
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

#get user by ID
user.getPk(1)
print user.toJSON()
row = user.salario.get()
print Models.serialize(row)