ARG VERSION=dev
FROM instituutnederlandsetaal/taggers-dockerized-base:$VERSION

COPY requirements.sh requirements.txt nltk-download.py ./
RUN ./requirements.sh && python3 nltk-download.py

COPY --link process.py /
COPY --link model.config /
COPY --link /lemmatizer ./lemmatizer
COPY --link /lexicon ./lexicon
COPY --link /huggingface/lemmatizer ./huggingface/lemmatizer
COPY --link /huggingface/tagging ./huggingface/tagging
