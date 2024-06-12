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

# Huggingface
# Commented for now, as we need Git LFS to build these. Perhaps in the future.
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-base:$VERSION_LABEL huggingface/base
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-1400-1600:$VERSION_LABEL huggingface/TDN-1400-1600
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-1600-1900:$VERSION_LABEL huggingface/TDN-1600-1900
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-all:$VERSION_LABEL huggingface/TDN-ALL
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-all-enhanced:$VERSION_LABEL huggingface/TDN-ALL-ENHANCED
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-bab:$VERSION_LABEL huggingface/TDN-BAB
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-clvn:$VERSION_LABEL huggingface/TDN-CLVN
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-cour:$VERSION_LABEL huggingface/TDN-COUR
# docker build -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-dbnldq:$VERSION_LABEL huggingface/TDN-DBNLDQ
