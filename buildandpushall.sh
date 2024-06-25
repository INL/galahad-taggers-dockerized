# Set the default label
: ${VERSION_LABEL:=dev}

echo "Will build taggers with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

./buildall.sh

# PIE
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1400-1600:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1600-1900:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-all:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-bab:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-clvn:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-cour:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-dbnldq:$VERSION_LABEL

# Huggingface
# Commented for now, as we need Git LFS to build these. Perhaps in the future.
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-1400-1600:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-1600-1900:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-all:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-all-enhanced:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-bab:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-clvn:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-cour:$VERSION_LABEL
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-dbnldq:$VERSION_LABEL
