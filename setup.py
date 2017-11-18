from setuptools import setup

setup(
    name='simple',
    packages=['simple'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
