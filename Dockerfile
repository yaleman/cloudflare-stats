FROM python:3.10-slim

#Set the working directory
WORKDIR /usr/src/app

COPY pyproject.toml .
COPY uv.lock .

#copy all the files
RUN mkdir cloudflare_stats
RUN ls -la
COPY cloudflare_stats cloudflare_stats/

RUN python -m pip install uv

USER nobody

#Run the command
CMD [ "uv", "run", "cloudflare-analytics" ]