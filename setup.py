from setuptools import setup, find_packages

setup(
    name="sphinxweb",
    version="0.1.1",
    url='https://github.com/shimizukawa/sphinx-websupport-app',
    author="Jacob Mason",
    author_email="noreply@example.org",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-OpenID',
        'Flask-Mail',
        'SQLAlchemy',
        'alembic',
        'Sphinx',
    ],
    entry_points={
        'console_scripts': [
            'sphinxweb-build=sphinxweb.build:main',
            'sphinxweb-runserver=sphinxweb.runserver:main',
            'sphinxweb-make-moderator=sphinxweb.make_moderator:main',
            'sphinxweb-make-user-permission=sphinxweb.make_user_permission:main',
        ]
    },
)
