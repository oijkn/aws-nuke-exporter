FROM ubuntu:22.04

COPY docker_files/dkr-pkglist .

RUN apt-get -y update && apt-get -y upgrade && apt-get install $(cat dkr-pkglist) -y && \
  apt-get -y clean && rm -rf /var/lib/apt/lists/*

RUN pip install aws-nuke-exporter

ENTRYPOINT [ "aws-nuke-exporter" ]

