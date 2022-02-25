__version__ = '0.1.13.dev0'

import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

install_requires = [
    'plaster_pastedeploy',
    'pyramid~=2.0',
    'Chameleon',
    'pyramid_chameleon',
    'pyramid_beaker',
    'alembic',
    'pyramid_tm',
    'pyramid_mailer',
    'SQLAlchemy~=1.4',
    'transaction',
    'zope.sqlalchemy>=1.6',
    'psycopg2',
    'pytz',
    'rutter',
    'marshmallow',
    'bcrypt',
    'file-magic',
    'saexts',
    'hashids',
]

extra_requires = {
    'production': [
        'gunicorn'
    ],
    'development': [
        'pyramid_debugtoolbar',
        'waitress',
    ],
    'testing': [
        'WebTest >= 1.3.1',  # py3 compat
        'pytest >= 3.7.4',
        'pytest-cov',
    ]
}

setup(
    name='amnesiacms',
    version=__version__,
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
    install_requires=install_requires,
    extras_require=extra_requires,
    entry_points={
        'paste.app_factory': [
            'main = amnesia:main'
        ],
        'console_scripts': [
            'initialize_amnesia_db = amnesia.scripts.initializedb:main',
            'initialize_amnesia_mime = amnesia.scripts.initializemime:main',
            'build_statics = amnesia.scripts.build_statics:main',
            'fix_files = amnesia.scripts.fix_file_paths:main',
        ]
    }
)
