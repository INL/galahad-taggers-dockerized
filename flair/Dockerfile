ARG VERSION
FROM instituutnederlandsetaal/taggers-dockerized-base:$VERSION
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c 'from flair.nn import Classifier; Classifier.load("flair/upos-multi"); Classifier.load("flair/ner-dutch-large")'
COPY --link process.py /