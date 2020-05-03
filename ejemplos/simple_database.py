# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Sep-2017
# @License: Apache license vesion 2.0

import os
import sys
import names
import random
from random_word import RandomWords
import datetime
random.seed()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from valleorm import  models
from valleorm.models.tools import Q

class Publication(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Article(models.Model):
    headline = models.CharField(max_length=100)
    publications = models.ManyToManyField(Publication)

    class Meta:
        ordering = ['headline']

    def __str__(self):
        return self.headline


class TestNullFields(models.Model):
   char_can_null = models.CharField(max_length=20, null=True)
   char__default_not_null = models.CharField(max_length=12, default="caracola")

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

def create_musician_data(r):
   
   instruments = ["accordion", "acoustic guitar", "bagpipes", "banjo"]
   for i in range(0,r):
      random.seed()
      print("Creando musician %s" % i+1)
      m = Musician()
      m.first_name = names.get_first_name()
      m.last_name = names.get_last_name()
      m.instrument = random.choice(instruments)
      m.save()
      print()
      cerate_album_data(m)

def cerate_album_data(m):
   r = random.randint(0, 10)
   for i in range(0, r):
      print("Creando album %s" % i+1)
      random.seed()
      a = Album()
      a.name = names.get_first_name()
      a.num_stars = random.randint(0,10)
      a.release_date = datetime.datetime.now()
      m.album.add(a)


if __name__ == "__main__":
   '''
   import time
   instruments = ["accordion", "acoustic guitar", "bagpipes", "banjo"]
   print("Borrando base de datos completa....")
   models.Utility.drop_db()
   print("Creando base de datos con Tablas Musician, Album")
   models.migrate_models(models=[Musician, Album])
   print("Creando datos aleatoreos")
   create_musician_data(20)
   '''

   m = Album.getByPk(12).artist.get()
   print(m.toJSON())