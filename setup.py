from setuptools import setup, find_packages

setup(
    name='nexpose',
    version='0.1',
    packages=find_packages(exclude=['test']),
    install_requires=['requests', 'mypy_lang', 'lxml'],
)
