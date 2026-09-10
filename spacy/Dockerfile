ARG VERSION=dev

FROM instituutnederlandsetaal/galahad-taggers:$VERSION

ARG CPU_GPU=cpu
ENV CPU_GPU=$CPU_GPU

ARG SPACY_MODEL
ENV SPACY_MODEL=$SPACY_MODEL

COPY --link process.py conllu_tei_helper.py ./
RUN --mount=type=bind,source=requirements/$CPU_GPU.txt,target=/requirements.txt \
    apt update && apt install libgomp1 -y && pip install --no-deps --no-cache-dir -r requirements.txt && python3 -m spacy download $SPACY_MODEL
