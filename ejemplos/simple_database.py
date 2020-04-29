# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0


import os
import sys
import names
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from valleorm import  models


class TestFields(models.Model):
   char = models.CharField(max_length=100)
   text = models.TextField()
   date = models.DateField(auto_now_add=True)
   date_time = models.DateTimeField(auto_now=True)
   boolean = models.BooleanField()
   integer = models.IntegerField()
   decimal = models.DecimalField(5,2)


class Person(models.Model):
   first_name = models.CharField(max_length=30)
   last_name = models.CharField(max_length=30)
   casado  = models.BooleanField()



class Musician(models.Model):
   first_name = models.CharField(max_length=50)
   last_name = models.CharField(max_length=50)
   instrument = models.CharField(max_length=100)

class Album(models.Model):
   artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
   name = models.CharField(max_length=100)
   release_date = models.DateField()
   num_stars = models.IntegerField()


def create_person_data():
   for i in range(0, 10):
      user =  Person()
      user.first_name = names.get_first_name()
      user.last_name = names.get_first_name()
      user.save()

def create_musician_data():
   import random
   from random_word import RandomWords
   import datetime
   random.seed()
   instruments = ["accordion", "acoustic guitar", "bagpipes", "banjo"]
   for i in range(0,10):
      m = Musician()
      m.first_name = names.get_first_name()
      m.last_name = names.get_last_name()
      m.instrument = random.choice(instruments)
      m.save()
      a = Album()
      a.name = names.get_last_name()
      a.release_date = datetime.datetime.now()
      a.num_stars = random.randint(0,10)
      a.artist = m
      a.save()


if __name__ == "__main__":
   import random
   from random_word import RandomWords
   import datetime
   random.seed()
   instruments = ["accordion", "acoustic guitar", "bagpipes", "banjo"]
   
   ps = TestFields.find()
   for p in ps:
      print(p.toJSON())
   