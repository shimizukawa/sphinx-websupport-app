FROM shimizukawa/sphinx-dev:latest

COPY . /source
WORKDIR /source
VOLUME /source

RUN pip install -U -r /source/requirements.txt

CMD ["sphinx-build", "-M", "html", "/source/source", "/source/build", "-N"]

