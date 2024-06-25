# Set the default label
: ${VERSION:=latest}

echo "Will build taggers with version <$VERSION>. Set VERSION to override this."

# Base image
docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-base:$VERSION base

# PIE
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-base:$VERSION pie/base
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-1400-1600:$VERSION pie/TDN-1400-1600
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-1600-1900:$VERSION pie/TDN-1600-1900
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-all:$VERSION pie/TDN-ALL
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-bab:$VERSION pie/TDN-BAB
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-clvn:$VERSION pie/TDN-CLVN
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-cour:$VERSION pie/TDN-COUR
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-pie-tdn-dbnldq:$VERSION pie/TDN-DBNLDQ

# Huggingface
# Commented for now, as we need Git LFS to build these. Perhaps in the future.
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-base:$VERSION huggingface/base
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-1400-1600:$VERSION huggingface/TDN-1400-1600
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-1600-1900:$VERSION huggingface/TDN-1600-1900
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-all:$VERSION huggingface/TDN-ALL
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-all-enhanced:$VERSION huggingface/TDN-ALL-ENHANCED
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-bab:$VERSION huggingface/TDN-BAB
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-clvn:$VERSION huggingface/TDN-CLVN
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-cour:$VERSION huggingface/TDN-COUR
# docker build --build-arg VERSION=$VERSION -t instituutnederlandsetaal/taggers-dockerized-hug-tdn-dbnldq:$VERSION huggingface/TDN-DBNLDQ
