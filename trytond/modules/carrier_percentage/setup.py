#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from setuptools import setup
import re
import os
import ConfigParser


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' %
            (dep, major_version, minor_version, major_version,
                minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1))

tests_require = ['proteus >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1),
    'trytond_purchase_shipment_cost >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1),
    'trytond_sale_shipment_cost >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1)]
dependency_links = []
if minor_version % 2:
    # Add development index for testing with proteus
    dependency_links.append('https://trydevpi.tryton.org/')

setup(name='trytond_carrier_percentage',
    version=info.get('version', '0.0.1'),
    description='Tryton module to add cost method "on percentage" on carrier',
    long_description=read('README'),
    author='Tryton',
    url='http://www.tryton.org/',
    download_url=("http://downloads.tryton.org/" +
        info.get('version', '0.0.1').rsplit('.', 1)[0] + '/'),
    package_dir={'trytond.modules.carrier_percentage': '.'},
    packages=[
        'trytond.modules.carrier_percentage',
        'trytond.modules.carrier_percentage.tests',
        ],
    package_data={
        'trytond.modules.carrier_percentage': (info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', 'tests/*.rst']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: Bulgarian',
        'Natural Language :: Czech',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    install_requires=requires,
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    carrier_percentage = trytond.modules.carrier_percentage
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    tests_require=tests_require,
    )
