from setuptools import setup, find_packages

setup(
    name='preciseLake',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'networkx',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'preciseLake=preciseLake.preciseLake:main',
        ],
    },
    author='Shreya Shree S',
    author_email='shreyashree00015@gmail.com',
    description='A code health analyzer that also visualizes the structure.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shreyashree00015/preciseLake',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
