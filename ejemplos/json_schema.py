# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


# -*- coding: utf-8 -*-
# allow direct execution
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm.models import Model
Model.GLOBAL_DB_NAME = "../json_schema.db"

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
Model.dropDB(Model.GLOBAL_DB_NAME)
user = Model(tableName= "user",  model=modelUser)
sal = Model(tableName= "salario",  model=modelSalario)

user.mail = "wwwkk@loco.com"
user.nombre = "El loco pitres"
user.apellido = "Fuertes"
user.save()

sal.mes = "may"
sal.salario = "1400"
user.salario.add(sal)
sal = Model(tableName= "salario",  model=modelSalario)
sal.mes = "jun"
sal.salario = "1400"
user.salario.add(sal)
sal = Model(tableName= "salario",  model=modelSalario)
sal.mes = "jul"
sal.salario = "1400"
user.salario.add(sal)
sal = Model(tableName= "salario",  model=modelSalario)
sal.mes = "ago"
sal.salario = "1400"
user.salario.add(sal)

#get user by ID
user.load_by_pk(1)
print user.toJSON()
row = user.salario.get()
print Model.serialize(row)
