# @Author: Manuel Rodriguez <valle>
# @Date:   17-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: test.py
# @Last modified by:   valle
# @Last modified time: 17-Aug-2017
# @License: Apache license vesion 2.0


add = {
    'add':{
        'db': "hola",
        'parent':{
            'nombre': 'lolo',
            'hijos':[
                {'nieto':{'nombre': 'dani'}},
                {'nieto':{'nombre': 'felipe'}}
            ]
        }
    }
}

print add

print type(add['add']['parent']['hijos'][0])
