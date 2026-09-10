ARG VERSION=dev

FROM instituutnederlandsetaal/galahad-taggers:$VERSION

ARG CPU_GPU=cpu
ENV CPU_GPU=$CPU_GPU

ARG SPACY_MODEL
ENV SPACY_MODEL=$SPACY_MODEL

ENV LD_LIBRARY_PATH=/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib

COPY --link process.py conllu_tei_helper.py ./
RUN --mount=type=bind,source=requirements/$CPU_GPU.txt,target=/requirements.txt \
    apt update && apt install libgomp1 -y && \
    pip install --no-deps --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu126 && \
    python3 -m spacy download $SPACY_MODEL
