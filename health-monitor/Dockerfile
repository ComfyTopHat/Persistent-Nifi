FROM python:3.9

USER root
RUN mkdir temp
RUN pip install requests

COPY ./scripts/initializeNifi.py /temp
COPY ./scripts/nifi_manager.py /temp

ENTRYPOINT ["python", "/temp/initializeNifi.py" ]