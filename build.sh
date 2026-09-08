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
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-pie:cpu-$VERSION pie/base
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-pie:gpu-$VERSION pie/base
# tdn-all
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-all:cpu-$VERSION pie/TDN-ALL
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-all:gpu-$VERSION pie/TDN-ALL
# tdn-1200-1600
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1200-1600:cpu-$VERSION pie/TDN-1200-1600
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1200-1600:gpu-$VERSION pie/TDN-1200-1600
# tdn-1600-1900
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1600-1900:cpu-$VERSION pie/TDN-1600-1900
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-pie-tdn-1600-1900:gpu-$VERSION pie/TDN-1600-1900

# UD-parsers
# flair
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-flair:cpu-$VERSION flair
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-flair:gpu-$VERSION flair
# # spacy
docker build --build-arg VERSION=$VERSION --build-arg SPACY_MODEL=nl_core_news_lg --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-spacy:cpu-$VERSION spacy
docker build --build-arg VERSION=$VERSION --build-arg SPACY_MODEL=nl_core_news_lg --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-spacy:gpu-$VERSION spacy
# stanza
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=cpu -t instituutnederlandsetaal/galahad-taggers-stanza:cpu-$VERSION stanza
docker build --build-arg VERSION=$VERSION --build-arg CPU_GPU=gpu -t instituutnederlandsetaal/galahad-taggers-stanza:gpu-$VERSION stanza
# udpipe
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/galahad-taggers-udpipe:$VERSION udpipe

# Huggingface
# TODO
