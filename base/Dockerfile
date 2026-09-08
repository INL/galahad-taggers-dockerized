FROM python:3.12.9-slim-bookworm

ARG CPU_GPU=cpu
ENV CPU_GPU=$CPU_GPU
ENV LD_LIBRARY_PATH=:/usr/local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/usr/local/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.12/site-packages/nvidia/cufft/lib:/usr/local/lib/python3.12/site-packages/nvidia/curand/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparse/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusparselt/lib:/usr/local/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/usr/local/lib/python3.12/site-packages/nvidia/cusolver/lib

COPY --link . ./
RUN pip install --no-deps --no-cache-dir uv && uv --no-cache pip install --system --no-deps --index-strategy=unsafe-best-match --no-cache-dir -r requirements/$CPU_GPU.txt && ./fix-cuda-env.sh && uv cache clean

EXPOSE 8080

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install --no-deps --no-cache -r requirements.txt
COPY --link *.py ./

CMD ["python", "-u", "webservice.py"]
