# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   17-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: ejemplo_helper.py
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import names

from valleorm.models.qsonhelper  import  QSonHelper

QSon1 = {
    'add':{
        'db': 'test_qson',
        'user': [{
             'name': 'manolo',
             'apellido': 'rodriguez'
             },
             {
            'ID': 1,
            'direccion':{
                'calle': 'Avd. Francisco Aylala',
                'numero': 85
            }
         }]
        }
     }

QSon2 = {
    'get':{
        'db': 'test_qson',
        'user':{
            'direccion':{}
         }
        }
     }


QSon3 = {
    'add':{
    'db': 'test_qson',
    'user':{
            'name': names.get_first_name(),
            'apellido': names.get_last_name()
        }}
}



QSon4 = {
    "get":{
        'db': 'test_qson',
            'user': {
            }
        }
}

QSon5 = {
    "rm":{
        'db': 'test_qson',
            'user': {
                'ID': 5
            }
        }
}
 
qsonheler = QSonHelper(path="../")
print (qsonheler.decode_qson(QSon4))
