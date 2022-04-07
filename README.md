# cloudflare-stats

This pulls information from CloudFlare and shoves it into my Splunk instance.

## Installation

Install this library using `pip`:

    $ python -m pip install git+https://github.com/yaleman/cloudflare-stats

## Usage

Configuration:

Copy `cloudflare-stats.example.json` to `cloudflare-stats.json` and put in your details.

Running this in docker:

```shell
docker run --rm -it \
    -v "$HOME/.config/cloudflare-stats.json:/etc/cloudflare-stats.json" \
    ghcr.io/yaleman/cloudflare-stats:latest
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    poetry install
    poetry shell
    cloudflare-analytics
