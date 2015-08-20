#!/usr/bin/env python
# encoding=utf-8
from setuptools import setup
import os
requirements = ['mwclient', 'gevent', 'markdown2']
path = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(path, 'README.md')).read()
setup(name='WikiTranslationBot',
      version='0.8.0.dev1',  # Rember to also update __ver__ in client.py
      description='MediaWiki API client',
      long_description=README,
      keywords='mediawiki spider translation',
      author='wgjak47',
      author_email='wgjak47@gmail.com',
      url='https://github.com/wgjak47/WikiTranslationSpider',
      license='MIT',
      packages=['WikiTranslationSpider'],
      install_requires=requirements,
      zip_safe=True
      )
