import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid<1.8',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy<1.1',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'pytz',
    ]

setup(name='amnesia',
      version='0.1',
      description='amnesia',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Julien Cigar',
      author_email='jcigar@ulb.ac.be',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='amnesia',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = amnesia:main
      [console_scripts]
      initialize_amnesia_db = amnesia.scripts.initializedb:main
      initialize_amnesia_mime = amnesia.scripts.initializemime:main
      """,
      )
