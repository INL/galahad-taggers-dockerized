# galahad-taggers-dockerized
GaLAHaD Taggers Dockerized provides a unified interface for linguistic annotation taggers to be added to GaLAHaD or to be run on their own. Tagger are containerized and can be accessed with an API in order to tag documents. Documents are queued and sent to a callback server once tagged.

[![Development images to Docker](https://github.com/INL/galahad-taggers-dockerized/actions/workflows/dev-to-docker.yml/badge.svg)](https://github.com/INL/galahad-taggers-dockerized/actions/workflows/dev-to-docker.yml)
[![Production images to Docker](https://github.com/INL/galahad-taggers-dockerized/actions/workflows/prod-to-docker.yml/badge.svg)](https://github.com/INL/galahad-taggers-dockerized/actions/workflows/prod-to-docker.yml)

### GaLAHaD-related Repositories
- [galahad](https://github.com/INL/galahad)
- [galahad-train-battery](https://github.com/INL/galahad-train-battery)
- [galahad-taggers-dockerized](https://github.com/INL/galahad-taggers-dockerized) [you are here]
- [galahad-corpus-data](https://github.com/INL/galahad-corpus-data/)
- [int-pie](https://github.com/INL/int-pie)
- [int-huggingface-tagger](https://github.com/INL/huggingface-tagger) [to be released]

This deployment architecture is developed for the project [GaLAHaD](https://github.com/INL/Galahad), but can also be run in standalone mode.

This repository refers to tagger models that have already been trained and are ready to be used in production. To train models, see [galahad-train-battery](https://github.com/INL/galahad-train-battery).

## Quick start
Clone this repository and its submodules.
```
git clone --recurse-submodules https://github.com/INL/galahad-taggers-dockerized
```
### Pull builds from Docker Hub
Do you have docker and docker compose? Do you have access to the public Docker Hub [instituutnederlandsetaal](https://hub.docker.com/repositories/instituutnederlandsetaal)? Then you can clone this repository and run

```
docker compose up
```

To run the taggers locally locally. The taggers are available on `localhost` with port equal to their devport. (You can find out the devport by looking at the port-forwards defined in `docker-compose.yml`)

Alternatively you can start specific taggers with:

```
docker compose up [SPECIFIC_TAGGER_1] [SPECIFIC_TAGGER_2]
```

### Local builds
Build the docker images: see `buildall.sh`.

### Connecting to an Galahad-like endpoint
If you want to connect the taggers to an endpoint outside of a docker network, you can specify a `.env.dev` file like

```
CALLBACK_SERVER=http://host.docker.internal:8010/internal/jobs
```

and use it instead of the default .env file like

```
docker compose --env-file .env.dev
```

### Without a GaLAHaD endpoint
These taggers can still be used without a GaLAHaD endpoint, in the form of a jobs API. See http://localhost:PORT for the tagger API. Simply don't define a callback server in the .env, or remove it from the docker compose environment variables.

## Creating your own tagger
To create your own tagger, use the base tagger as a starting point and overwrite `process.py`. I.e., start your Dockerfile with:
```
FROM instituutnederlandsetaal/taggers-dockerized-base:$VERSION
COPY --link process.py /
```
And fill out the process() and (optionally) init() functions of [base/process.py](https://github.com/INL/galahad-taggers-dockerized/blob/release/base/process.py).
The `in_file` points to a plain text file. Currently, your tagger is expected to produce tsv as output. The output tsv must contain a header with at least the columns 'token', 'lemma', 'pos' defined in any order.

### Running your own tagger
1. Define your tagger as a service in a docker compose file, say `your-tagger-dockerized.yml` . (You can use `docker-compose.yml` as guidance)
2. Make sure the tagger is in the `taggers-network` network. `your-tagger-dockerized.yml` should specify it as an external network and add your tagger to it:
   ```yaml
   services:
    my-tagger:
     ...
     ports:
      - 8091:8080 # optional devport
     networks:
      - taggers-network
   networks:
    taggers-network:
     external: true
   ```
3. Launch your tagger
   ```
   docker compose -f your-tagger-dockerized.yml up
   ```
   (add the optional `-d` flag to run in detached mode)

If you specified a devport, you can now find your tagger at `localhost` port devport.

### Make Galahad aware of your tagger
All that is left, is to add a yaml metadata file in the [server/data/taggers/](https://github.com/INL/galahad/tree/release/server/data/taggers) folder of Galahad. See the [Galahad repository](https://github.com/INL/galahad) for more details.
