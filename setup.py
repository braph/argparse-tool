#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='argparse-tool',
    version='0.0.0',
    author='Benjamin Abendroth',
    author_email='braph93@gmx.de',
    packages=['argparse_tool'], #find_packages(), #['argparse_tool'],
    scripts=['argparse-tool', 'argparse-tool-test'],
    description='Create shell completion scripts from pythons argument parser'
    #url='http://pypi.python.org/pypi/PackageName/',
    #license='LICENSE.txt',
    #long_description=open('README.txt').read(),
)
