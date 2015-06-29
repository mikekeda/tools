from setuptools import setup

setup(name='tools',
      version='0.4',
      description='Cool tools for developers',
      author='Voron',
      author_email='mriynuk@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Django==1.8.2',
                        'MySQL-python==1.2.5',
                        'Pillow==2.8.1',
                        'Unidecode==0.04.17',
                        'argparse==1.2.1',
                        'backports.ssl-match-hostname==3.4.0.2',
                        'certifi==2015.04.28',
                        'tornado==4.2',
                        'wsgiref==0.1.2'],
      )
