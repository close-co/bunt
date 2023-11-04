from setuptools import setup, find_packages


setup(
   name='bunt',
   version='1.0',
   description='A module for tagging the color of the products in the images.',
   author='Valentina Feruere',
   author_email='valentinaferuere@close.com.co',
   packages=find_packages(),
   install_requires=[
      'click',
      'ex'
   ],
   entry_points={
      'console_scripts': [
         'bunt=bunt.cli:cli',
      ],
   },
)