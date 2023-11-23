from setuptools import setup, find_packages

setup(
    name='aws-nuke-exporter',
    version='1.0.0',
    author='oijkn',
    author_email='peacefull64@hotmail.fr',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aws-nuke-exporter=aws_nuke_exporter.exporter:main',
        ],
    },
    url='https://github.com/oijkn/aws-nuke-exporter',
    license='GPL',
    description='A tool for exporting aws-nuke logs in JSON or CSV formats.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
