from setuptools import setup

setup(
    name="Sphinx WebSupport Demo",
    version="0.1.0",
    url='https://bitbucket.org/masklinn/sphinx-demo-webapp',
    author="Jacob Mason",
    author_email="noreply@example.org",
    maintainer="Xavier Morel",
    maintainer_email="noreply@example.org",
    packages=['sphinxweb', 'sphinxweb.views'],
    scripts=['build.py', 'runserver.py', 'make-moderator.py'],
    install_requires=[
        'Flask',
        'Flask-OpenID',
        'Flask-Mail',
        'SQLAlchemy',
        'Sphinx',
    ]
)
