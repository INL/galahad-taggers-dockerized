ARG VERSION=dev
FROM instituutnederlandsetaal/taggers-dockerized-base:$VERSION

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --link process.py /
COPY --link pie/ ./pie/