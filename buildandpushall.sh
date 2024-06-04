# Set the default label
: ${VERSION_LABEL:=dev}

echo "Will build taggers with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

./buildall.sh

# Base image
docker push instituutnederlandsetaal/taggers-dockerized-base:$VERSION_LABEL

# PIE
docker push instituutnederlandsetaal/taggers-dockerized-pie-base:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1400-1600:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-1600-1900:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-all:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-bab:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-clvn:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-cour:$VERSION_LABEL
docker push instituutnederlandsetaal/taggers-dockerized-pie-tdn-dbnldq:$VERSION_LABEL
