# coding=utf-8

from setuptools import setup, find_packages


long_description = ''

try:
  import requests
  r = requests.post(url='http://c.docverter.com/convert',
                    data={'to':'rst','from':'markdown'},
                    files={'input_files[]':open('README.md','rb')})
  if r.ok:
    long_description = r.content

except:
  pass

setup(
	name = 'valleorm',
	version = '1.0.0.3',
	author = 'Manuel Rodriguez',
	author_email = 'valle.mrv@gmail.com',
	description = 'Es una orm simple, con modelos JSON o derivados de la clase Models',
	long_description = long_description,
	url = 'https://github.com/vallemrv/orm-python-sqlite',
	packages = find_packages(),
	test_suite = 'tests',
	classifiers = [
    	'Development Status :: 5 - Production/Stable',
    	'Intended Audience :: Developers',
    	'Intended Audience :: Information Technology',
    	'Programming Language :: Python',
    	'Programming Language :: Python :: 2.6',
    	'Programming Language :: Python :: 2.7',
    	'Programming Language :: Python :: 3.2',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    	'License :: OSI Approved :: Apache Software License'
    	]
	)
