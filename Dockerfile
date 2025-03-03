FROM python:3.10-slim

#Set the working directory
WORKDIR /usr/src/app

COPY pyproject.toml .
COPY uv.lock .

#copy all the files
RUN mkdir cloudflare_stats
RUN ls -la
COPY cloudflare_stats cloudflare_stats/

RUN apt-get update && apt-get -y install git

RUN python -m pip install uv
RUN useradd  --user-group  --create-home cloudflare
RUN chown -R cloudflare:cloudflare /usr/src/app
USER cloudflare
RUN uv sync

USER root
RUN apt-get -y purge git && apt-get clean

USER cloudflare
#Run the command
CMD [ "uv", "run", "cloudflare-analytics" ]