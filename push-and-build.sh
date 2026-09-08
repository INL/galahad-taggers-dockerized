# load the .env file
source .env

# Set the default label
: ${VERSION:=latest}
: ${CPU_GPU:=cpu}

echo "Will build taggers with version <$VERSION> and CPU_GPU <$CPU_GPU>. Set .env to override this."


# PIE
docker push instituutnederlandsetaal/galahad-taggers-pie-tdn-1200-1600:$CPU_GPU-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-pie-tdn-1600-1900:$CPU_GPU-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-pie-tdn-all:$CPU_GPU-$VERSION
# UD-parsers
# docker push instituutnederlandsetaal/galahad-taggers-udpipe:$VERSION
docker push instituutnederlandsetaal/galahad-taggers-spacy:cpu-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-spacy:gpu-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-stanza:cpu-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-stanza:gpu-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-flair:cpu-$VERSION
docker push instituutnederlandsetaal/galahad-taggers-flair:gpu-$VERSION

# Huggingface
# Commented for now, as we need Git LFS to build these. Perhaps in the future.
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-1400-1600:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-1600-1900:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-all:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-all-enhanced:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-bab:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-clvn:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-cour:$VERSION
# docker push instituutnederlandsetaal/galahad-taggers-hug-tdn-dbnldq:$VERSION
