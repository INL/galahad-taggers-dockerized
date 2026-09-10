FROM python:3.12.14-slim-trixie

EXPOSE 8080

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install --no-deps --no-cache -r requirements.txt
COPY --link *.py ./

CMD ["python", "-u", "webservice.py"]
