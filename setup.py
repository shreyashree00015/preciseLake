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
    author='Your Name',
    author_email='your.email@example.com',
    description='A code health analyzer that checks for various code issues and visualizes the code structure.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/preciseLake',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
