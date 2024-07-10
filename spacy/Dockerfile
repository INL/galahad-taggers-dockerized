ARG tag=latest
FROM instituutnederlandsetaal/taggers-dockerized-base:$tag as tagger_base

FROM nvidia/cuda:12.5.0-runtime-ubuntu22.04

# set up environment
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl
RUN apt-get install unzip
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

# Upgrade python and pip
RUN apt update
RUN apt upgrade -y python3
RUN pip3 install --upgrade pip

# Check the python version and pip version
RUN python3 --version
RUN pip3 --version

ARG SPACY_MODEL
ENV SPACY_MODEL=${SPACY_MODEL}

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download ${SPACY_MODEL}

COPY --from=tagger_base timeout.py /
COPY --from=tagger_base shared.py /
COPY --from=tagger_base start.sh /

COPY --link process.py /
COPY --link tagger_worker.py /
COPY --link tei2trankit.py /
COPY --link statuslogger.py /
COPY --link webservice.py /

RUN mkdir input status output process

EXPOSE 8080

CMD ["./start.sh"]