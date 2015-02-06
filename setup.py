from setuptools import setup



setup(
    name='orm.py',
    version='0.1',
    description='A minimal ORM for postgres',
    long_description=open('README.md').read(),
    url='https://github.com/pscohn/orm.py',
    author='Paul Cohn',
    email='pscohn@gmail.com',
    license='MIT',
    keywords='orm object relational mapper postgres postgresql',
    install_requires=['psycopg2'],
    
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Database :: Front-Ends',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.4',
    ],


)







