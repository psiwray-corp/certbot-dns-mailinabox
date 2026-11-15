from pathlib import Path

from setuptools import setup

here = Path(__file__).parent

setup(
    name="certbot-dns-mailinabox",
    version="0.1.0",
    description="Mail-in-a-Box's DNS authenticator.",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Ψray Corp",
    url="https://github.com/psiwray-corp/certbot-dns-mailinabox",
    project_urls={
        "Source": "https://github.com/psiwray-corp/certbot-dns-mailinabox",
        "Issues": "https://github.com/psiwray-corp/certbot-dns-mailinabox/issues",
    },
    license="MIT",
    py_modules=["certbot_dns_mailinabox"],
    install_requires=[
        "certbot>=2.0.0",
        "pyotp",
        "requests",
    ],
    python_requires=">=3.10",
    keywords=["certbot", "letsencrypt", "dns-01", "mail-in-a-box"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Systems Administration",
    ],
    entry_points={
        "certbot.plugins": [
            "dns-mailinabox = certbot_dns_mailinabox:Authenticator",
        ],
    },
)
