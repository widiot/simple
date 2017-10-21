from setuptools import setup

setup(
    name='simpleblog',
    packages=['simpleblog'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
