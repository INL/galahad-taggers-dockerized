ARG VERSION=dev

FROM instituutnederlandsetaal/galahad-taggers:$VERSION

ARG CPU_GPU=cpu
ENV CPU_GPU=$CPU_GPU

RUN --mount=type=bind,source=requirements/$CPU_GPU.txt,target=/requirements.txt \
    pip install --no-deps --no-cache-dir -r requirements.txt \
    --extra-index-url "$([ "$CPU_GPU" = "gpu" ] && echo https://download.pytorch.org/whl/cu126 || echo https://download.pytorch.org/whl/cpu)"
COPY --link . ./
