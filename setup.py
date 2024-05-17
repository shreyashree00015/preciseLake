# setup.py

from setuptools import setup, find_packages

setup(
    name='preciseLake',
    version='1.0.0',
    description='A code health analysis and optimization feedback tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shreyashree00015/preciseLake',
    author='Shreya Shree S',
    author_email='shreyashree00015@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
