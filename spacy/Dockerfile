ARG VERSION
FROM instituutnederlandsetaal/taggers-dockerized-base:$VERSION as tagger_base

FROM nvidia/cuda:12.5.0-runtime-ubuntu22.04

# set up environment
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl nano unzip
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

# Upgrade python and pip
RUN apt update
RUN apt upgrade -y python3
RUN pip3 install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ARG SPACY_MODEL
ENV SPACY_MODEL=${SPACY_MODEL}
RUN python3 -m spacy download ${SPACY_MODEL}

COPY --from=tagger_base timeout.py /
COPY --from=tagger_base shared.py /
COPY --from=tagger_base start.sh /
COPY --from=tagger_base tagger_worker.py /
COPY --from=tagger_base statuslogger.py /
COPY --from=tagger_base webservice.py /

COPY --link process.py /
COPY --link tei2trankit.py /

RUN mkdir input status output process

EXPOSE 8080

CMD ["./start.sh"]