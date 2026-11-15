from setuptools import setup

setup(
    name="certbot-dns-mailinabox",
    version="0.1.0",
    description="Mail-in-a-Box's DNS authenticator.",
    py_modules=["certbot_dns_mailinabox"],
    install_requires=[
        "certbot",
        "pyotp",
        "requests",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-mailinabox = certbot_dns_mailinabox:Authenticator",
        ],
    },
)
