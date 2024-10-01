# Set the default label
: ${VERSION:=latest}

echo "Will build taggers with version <$VERSION>. Set VERSION to override this."

# Base image
docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-base:$VERSION base

# ud-parsers
docker build --build-arg VERSION=$VERSION --build-arg SPACY_MODEL=nl_core_news_lg -t instituutnederlandsetaal/taggers-dockerized-spacy:$VERSION spacy
docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-stanza:$VERSION stanza
docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-flair:$VERSION flair
