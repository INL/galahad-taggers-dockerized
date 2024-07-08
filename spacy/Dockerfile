ARG tag=latest
FROM instituutnederlandsetaal/taggers-dockerized-base:$tag
ARG SPACY_MODEL
ENV SPACY_MODEL=${SPACY_MODEL}
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download ${SPACY_MODEL}
COPY --link process.py /
COPY --link tei2trankit.py /