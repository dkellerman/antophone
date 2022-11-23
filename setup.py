from setuptools import setup
setup(
    name='Antophone',
    app=["main.py"],
    data_files=['images/ant.png'],
    setup_requires=["py2app"],
)
