FROM python:3.10-slim-bookworm
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
	&& mkdir input status output process
COPY --link . ./

# Optionally set a callback server
# ENV CALLBACK_SERVER=http://localhost:8010

EXPOSE 8080

CMD ["./start.sh"]