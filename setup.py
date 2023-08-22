from setuptools import find_packages, setup

setup(
    name='recup_rocrate_lib',
    packages=find_packages(include=['recup_rocrate_lib']),
    version='0.1.0',
    description='Utilities for parsing Chimbuko provenance database files into ROCrate JSON Metadata.',
    author="Polina Shpilker",
    license="MIT",
    install_requires=['rocrate', 'provdb_python', 'pymargo']
)