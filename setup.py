from setuptools import setup, find_packages

setup(
    name = 'valleorm',
	version = '1.2.3',
	author = 'Manuel Rodriguez',
	author_email = 'valle.mrv@gmail.com',
	description = 'Orm simple al estilo django. Es compatible los modelos basicos creados en django.',
    packages=['valleorm', "valleorm.models"],
    url='https://github.com/vallemrv/python-ormsqlite',
    license='LICENSE',
    long_description=open('README.txt').read(),
)