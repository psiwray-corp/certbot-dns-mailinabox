from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration

from pyotp import TOTP

from requests import codes, delete, post
from requests.exceptions import RequestException

from typing import Any
from typing import Callable
from typing import Optional
from typing import cast

from time import sleep


class Authenticator(dns_common.DNSAuthenticator):
    """Mail-in-a-Box's DNS authenticator."""

    description = "Mail-in-a-Box's DNS authenticator."

    HTTP_TIMEOUT_SECONDS = 30
    RETRYABLE_STATUS_CODES = frozenset({
        codes.unauthorized,
        codes.too_many_requests,
        codes.internal_server_error,
        codes.bad_gateway,
        codes.service_unavailable,
        codes.gateway_timeout,
    })

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 10) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="Mail-in-a-Box credentials INI file.")
        add("host", help="The Mail-in-a-Box web interface host.")

    def more_info(self) -> str:
        return ("This plugin configures a DNS TXT record to respond to a DNS-01 "
                "challenge using the Mail-in-a-Box API.")

    def _setup_credentials(self) -> None:
        if not self.conf("host"):
            raise errors.PluginError(
                "The Mail-in-a-Box web interface host is required. "
                "Pass it with --dns-mailinabox-host."
            )
        self.credentials = self._configure_credentials(
            "credentials",
            "Mail-in-a-Box credentials INI file.",
            {
                "username": "User e-mail address",
                "password": "User password",
                "totp_secret": "Temporary one-time password secret for 2FA",
            },
        )

    def _get_credentials(self) -> CredentialsConfiguration:
        if self.credentials is None:  # pragma: no cover
            raise errors.Error("Plugin has not been prepared.")
        return self.credentials

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._change_record(post, validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._change_record(delete, validation_name, validation, missing_ok=True)

    def _change_record(
        self,
        request: Callable[..., Any],
        validation_name: str,
        validation: str,
        missing_ok: bool = False,
    ) -> None:
        """Create or delete the TXT record, retrying transient failures."""
        credentials = self._get_credentials()
        username = cast(str, credentials.conf("username"))
        password = cast(str, credentials.conf("password"))
        totp_secret = cast(str, credentials.conf("totp_secret"))
        retry_delay = float(TOTP(totp_secret).interval)

        url = f"https://{self.conf('host')}/admin/dns/custom/{validation_name}/txt"
        tries = 3
        while tries:
            tries -= 1
            try:
                response = request(
                    url,
                    auth=(username, password),
                    data=validation,
                    headers={"X-Auth-Token": TOTP(totp_secret).now()},
                    timeout=self.HTTP_TIMEOUT_SECONDS,
                )
            except RequestException as e:
                # Network errors and timeouts are worth retrying.
                if not tries:
                    raise errors.PluginError(
                        f"Could not reach the Mail-in-a-Box API at {url}: {e}"
                    ) from e
                sleep(retry_delay)
                continue

            status = response.status_code
            if status in (codes.ok, codes.no_content):
                return
            if missing_ok and status == codes.not_found:
                # Certbot's cleanup contract: a missing record is not an error.
                return
            if status in self.RETRYABLE_STATUS_CODES:
                # A 401 is most likely a stale TOTP code, so wait for the next
                # one; 429/5xx are transient server-side failures.
                if not tries:
                    raise errors.PluginError(
                        f"Mail-in-a-Box API request to {url} failed with HTTP {status}."
                    )
                sleep(retry_delay)
                continue
            raise errors.PluginError(
                f"Mail-in-a-Box API request to {url} failed with HTTP {status}."
            )
