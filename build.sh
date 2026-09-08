# load the .env file
source .env

# Set the default label
: ${VERSION:=latest}
: ${CPU_GPU:=cpu}

echo "Will build taggers with version <$VERSION> and CPU_GPU <$CPU_GPU>. Set .env to override this."

# Base image
docker build -t instituutnederlandsetaal/galahad-taggers:$VERSION base
# PIE
# base
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-pie:$CPU_GPU-$VERSION pie/base
# tdn-all
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-pie-tdn-all:$CPU_GPU-$VERSION pie/TDN-ALL
# tdn-1200-1600
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1200-1600:$CPU_GPU-$VERSION pie/TDN-1200-1600
# tdn-1600-1900
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1600-1900:$CPU_GPU-$VERSION pie/TDN-1600-1900

# UD-parsers
# flair
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-flair:$CPU_GPU-$VERSION flair
# # spacy
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU --build-arg SPACY_MODEL=nl_core_news_lg -t instituutnederlandsetaal/galahad-taggers-spacy:$CPU_GPU-$VERSION spacy
# stanza
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=$CPU_GPU -t instituutnederlandsetaal/galahad-taggers-stanza:$CPU_GPU-$VERSION stanza
# udpipe
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/galahad-taggers-udpipe:$VERSION udpipe

# Huggingface
# TODO
