# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm import models

class User(models.Model):
   nombre = models.CharField(max_length=100)
   mail = models.EmailField()
  
class Salario(models.Model):
  pass

class Puesto(models.Model):
  pass 