# Set the default label
: ${VERSION_LABEL:=dev}

echo "Will build taggers with version <$VERSION_LABEL>. Set VERSION_LABEL to override this."

# Base image
docker build -t instituutnederlandsetaal/taggers-dockerized-base:$VERSION_LABEL base

# PIE
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-base:$VERSION_LABEL pie/base
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-1400-1600:$VERSION_LABEL pie/TDN-1400-1600
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-1600-1900:$VERSION_LABEL pie/TDN-1600-1900
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-all:$VERSION_LABEL pie/TDN-ALL
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-bab:$VERSION_LABEL pie/TDN-BAB
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-clvn:$VERSION_LABEL pie/TDN-CLVN
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-cour:$VERSION_LABEL pie/TDN-COUR
docker build -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-dbnldq:$VERSION_LABEL pie/TDN-DBNLDQ
