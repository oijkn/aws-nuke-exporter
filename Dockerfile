FROM python:3.11-slim

RUN pip install aws-nuke-exporter

ENTRYPOINT [ "aws-nuke-exporter" ]

