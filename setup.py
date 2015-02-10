from setuptools import setup, find_packages

setup(
    name="sphinxweb",
    version="0.1.0",
    url='https://bitbucket.org/shimizukawa/sphinx-demo-webapp',
    author="Jacob Mason",
    author_email="noreply@example.org",
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-OpenID',
        'Flask-Mail',
        'SQLAlchemy',
        'Sphinx',
    ],
    entry_points={
        'console_scripts': [
            'sphinxweb-build=sphinxweb.build:main',
            'sphinxweb-runserver=sphinxweb.runserver:main',
            'sphinxweb-make-moderator=sphinxweb.make_moderator:main',
        ]
    },
)
