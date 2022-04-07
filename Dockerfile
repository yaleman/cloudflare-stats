FROM python:3.10-slim

#Set the working directory
WORKDIR /usr/src/app

COPY pyproject.toml .

#copy all the files
RUN mkdir cloudflare_stats
RUN ls -la
COPY cloudflare_stats cloudflare_stats/

RUN python -m pip install .

# RUN python -m pip uninstall -y poetry
#Expose the required port
# EXPOSE 5000

#Run the command
ENTRYPOINT [ "cloudflare-analytics"]