ARG tag=latest
FROM instituutnederlandsetaal/taggers-dockerized-base:$tag
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c 'import stanza; stanza.Pipeline(lang="nl", processors="tokenize,lemma,pos,depparse")'
COPY --link process.py /
COPY --link tei2trankit.py /