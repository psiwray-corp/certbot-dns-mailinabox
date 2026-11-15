# Certbot DNS plugin for Mail-in-a-Box

This plugin uses the DNS-01 authentication challenge with Mail-in-a-Box's DNS
API so that TXT records can be added and removed on the fly.

## Installation

Requires Python 3.10+ and certbot 2+.

```shell
python -m venv .venv
.venv/bin/pip install .
```

## Usage

Copy the sample credentials file and restrict its permissions:

```shell
cp credentials.ini.example credentials.ini
chmod 600 credentials.ini
```

Fill in an administrator account with 2FA enabled, then run:

```shell
certbot certonly -a dns-mailinabox \
	--dns-mailinabox-credentials credentials.ini \
	--dns-mailinabox-propagation-seconds 10 \
	--dns-mailinabox-host node.mxchgsvc.net \
	-d example.com
```

The host must be the one serving the Mail-in-a-Box web administration interface.

## Wildcard certificates

When a certificate covers both `example.com` and `*.example.com`, both DNS-01
challenges use the same `_acme-challenge.example.com` name. Mail-in-a-Box must
keep both TXT values at that name; verify this before relying on wildcard
issuance.
