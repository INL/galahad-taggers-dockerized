# Set the default label
: ${VERSION:=dev}

echo "Will build taggers with version <$VERSION>. Set VERSION to override this."

./buildall.sh

# PIE
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1400-1600:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1600-1900:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-all:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-bab:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-clvn:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-cour:$VERSION
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-dbnldq:$VERSION

# Huggingface
# Commented for now, as we need Git LFS to build these. Perhaps in the future.
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-1400-1600:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-1600-1900:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-all:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-all-enhanced:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-bab:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-clvn:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-cour:$VERSION
# docker push instituutnederlandsetaal/taggers-dockerized-hug-tdn-dbnldq:$VERSION
