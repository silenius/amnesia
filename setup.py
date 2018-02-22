# -*- coding: utf-8 -*-


import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

install_requires = [
    'pyramid~=1.9',
    'Chameleon>3.0',
    'pyramid_chameleon',
    'pyramid_beaker',
    'pyramid_tm',
    'pyramid_mailer',
    'SQLAlchemy~=1.2',
    'transaction',
    'zope.sqlalchemy',
    'psycopg2',
    'pytz',
    'rutter',
    'marshmallow>=3.0.0b7',
    'bcrypt',
    'file-magic',
    'saexts'
]

extra_requires = {
    'production': [
        'gunicorn'
    ],
    'development': [
        'pyramid_debugtoolbar',
        'waitress',
    ]
}

setup(
    name='amnesiacms',
    version='0.1.2',
    description='amnesia CMS',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Julien Cigar',
    author_email='julien@perdition.city',
    url='https://github.com/silenius/amnesia',
    keywords='web wsgi pyramid cms sqlalchemy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='amnesia',
    install_requires=install_requires,
    extras_require=extra_requires,
    entry_points={
        'paste.app_factory': [
            'main = amnesia:main'
        ],
        'console_scripts': [
            'initialize_amnesia_db = amnesia.scripts.initializedb:main',
            'initialize_amnesia_mime = amnesia.scripts.initializemime:main',
        ]
    }
)
