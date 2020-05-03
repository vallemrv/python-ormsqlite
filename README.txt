python-ormsqlite
I've done it to work with kivy and android. It works great with mobile devices. For people who do not seek much complexity. It is simple but you can perform more or less complex queries. Create a model quickly in seconds. Just create the model and you can create JSON queries.

package Installation
Install it via pip

$ [sudo] pip install valleorm

Or download zip and then install it by running

$ [sudo] python setup.py install

For kivy project only copy folder valleorm on root folder kivy project. And create your models simply.

Example from Class inheritance Models
from valleorm.models import models

lass Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)

class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()


m = Musician()
m.first_name = "Caracolo"
m.last_name = "tambolero"
m.instrument = "tambor"
m.save()

a = Album()
a.name = "delicias"
a.release_date = datetime.datetime.now()
a.num_starts = 10

m.album.add(m)

m = Musician.getByPk(1)
print(m.toJSON())

als = m.album.get()
from a in als:
   print(a.toJSON())
   
   
   
Condition example
m = Musician.filter(first_name="caracolo")
m = Musician.filter(first_name__contain="ca")
m = Musician.filter(first_name__between=("caracolo", "picopato"))

yum How to contribute
Have an idea? Found a bug? add a new issue or [fork] (https://github.com/vallemrv/orm-python-sqlite#fork-destination-box) and sendme a pull request. Don't forget to add your name to the Contributors section of this document.

scroll License
Licensed under the Apache-2.0, see LICENSE

heart_eyes Contributors
Manuel Rodriguez valle.mrv@gmail.com