# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   17-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: ejemplo_helper.py
# @Last modified by:   valle
# @Last modified time: 19-Aug-2017
# @License: Apache license vesion 2.0

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm.qsonhelper  import AddHelper, GetHelper

QSon1 = {
    'db': 'test_qson',
    'user': {
         'name': 'manolo',
         'apellido': 'rodriguez'
        }
     }

QSon2 = {
    'db': 'test_qson',
    'user': {
         'ID': 1,
         'hijo':[
             {'user':{
                 'name': "Manolo",
                 'apellido': "Ubrique",
                 'apodo': 'lolo'
             }}
         ]
        }
     }


QSon3 = {
    'db': 'test_qson',
    'user': {
        'ID': 1,
        'direccion':{
            'calle': 'Avd. Francisco Aylala',
            'numreo': 85
        }
     }
}

QSon4 = {
    'db': 'test_qson',
    'direccion':{
            'ID': 1,
            'localidad': 'Granada'
        }
}


QSon5 = {
    'db': 'test_qson',
    'user': {
         'name': 'Pepe luis',
        }
     }

QSearch = {
    'db': 'test_qson',
    'user': {
    }
}

QSearch1 = {
    'db': 'test_qson',
    'user': {
        'ID': 2,
    }
}
QSearch2 = {
    'db': 'test_qson',
    'user':{
    'direccion': {}
    }
}



def execute_add(QSon):
    Resutl = {}
    AddHelper(JSONQuery=QSon, JSONResult=Resutl)
    print Resutl

def execute_get(QSon):
    Resutl = {}
    GetHelper(JSONQuery=QSon, JSONResult=Resutl)
    print Resutl


execute_get(QSearch2)
