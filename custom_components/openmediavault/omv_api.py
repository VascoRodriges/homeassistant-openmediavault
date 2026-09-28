"""OpenMediaVault API."""

import json
import logging
from os import path
from typing import Any
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from threading import Lock
from time import time

import requests

_LOGGER = logging.getLogger(__name__)


# ---------------------------
#   load_cookies
# ---------------------------
def load_cookies(filename: str) -> dict | None:
    """Load cookies from file."""
    if path.isfile(filename):
        with open(filename, "rb") as f:
            return pickle_load(f)
    return None


# ---------------------------
#   save_cookies
# ---------------------------
def save_cookies(filename: str, data: dict):
    """Save cookies to file."""
    with open(filename, "wb") as f:
        pickle_dump(data, f)


# ---------------------------
#   OpenMediaVaultAPI
# ---------------------------
class OpenMediaVaultAPI(object):
    """Handle all communication with OMV."""

    def __init__(self, hass, host, username, password, use_ssl=False, verify_ssl=True):
        """Initialize the OMV API."""
        self._hass = hass
        self._host = host
        self._use_ssl = use_ssl
        self._username = username
        self._password = password
        self._protocol = "https" if self._use_ssl else "http"
        self._ssl_verify = verify_ssl
        if not self._use_ssl:
            self._ssl_verify = True
        self._resource = f"{self._protocol}://{self._host}/rpc.php"

        self.lock = Lock()

        self._connection = None
        self._cookie_jar = None
        self._cookie_jar_file = self._hass.config.path(".omv_cookies.json")
        self._connected = False
        self._reconnected = False
        self._connection_epoch = 0
        self._connection_retry_sec = 58
        self.error = None
        self.connection_error_reported = False
        self.accounting_last_run = None

    # ---------------------------
    #   has_reconnected
    # ---------------------------
    def has_reconnected(self) -> bool:
        """Check if API has reconnected."""
        if self._reconnected:
            self._reconnected = False
            return True

        return False

    # ---------------------------
    #   connection_check
    # ---------------------------
    def connection_check(self) -> bool:
        """Check if API is connected."""
        if not self._connected or not self._connection:
            if self._connection_epoch > time() - self._connection_retry_sec:
                return False

            if not self.connect():
                return False

        return True

    # ---------------------------
    #   disconnect
    # ---------------------------
    def disconnect(self, location="unknown", error=None):
        """Disconnect API."""
        if not error:
            error = "unknown"

        if not self.connection_error_reported:
            if location == "unknown":
                _LOGGER.error("OpenMediaVault %s connection closed", self._host)
            else:
                _LOGGER.error(
                    "OpenMediaVault %s error while %s : %s", self._host, location, error
                )

            self.connection_error_reported = True

        self._reconnected = False
        self._connected = False
        self._connection = None
        self._connection_epoch = 0

    # ---------------------------
    #   connect
    # ---------------------------
    def connect(self) -> bool:
        """Connect API."""
        self.error = None
        self._connected = False
        self._connection_epoch = time()
        self._connection = requests.Session()
        self._cookie_jar = requests.cookies.RequestsCookieJar()

        # Load cookies
        if cookies := load_cookies(self._cookie_jar_file):
            self._connection.cookies.update(cookies)

        self.lock.acquire()
        error = False
        try:
            response = self._connection.post(
                self._resource,
                data=json.dumps(
                    {
                        "service": "session",
                        "method": "login",
                        "params": {
                            "username": self._username,
                            "password": self._password,
                        },
                    }
                ),
                verify=self._ssl_verify,
            )

            if response.status_code != 200:
                error = True

            data = response.json()
            if data["error"] is not None:
                if not self.connection_error_reported:
                    _LOGGER.error(
                        "OpenMediaVault %s unable to connect: %s",
                        self._host,
                        data["error"]["message"],
                    )
                    self.connection_error_reported = True

                self.error_to_strings("%s" % data["error"]["message"])
                self._connection = None
                self.lock.release()
                return False

            resp = data["response"]

            # OMV >= 8.5.0 uses "status" string instead of "authenticated" bool
            if "authenticated" in resp:
                # Legacy schema (OMV < 8.5.0)
                authenticated = resp["authenticated"]
            elif "status" in resp:
                # New schema (OMV >= 8.5.0)
                authenticated = resp["status"] == "authenticated"
            else:
                # Unknown schema - log for debugging
                _LOGGER.warning(
                    "OpenMediaVault %s unexpected auth response schema: %s",
                    self._host,
                    list(resp.keys()),
                )
                authenticated = False

            if not authenticated:
                _LOGGER.error("OpenMediaVault %s authenticated failed", self._host)
                self.error_to_strings()
                self._connection = None
                self.lock.release()
                return False

        except requests.exceptions.ConnectionError as api_error:
            error = True
            self.error_to_strings("%s" % api_error)
            self._connection = None
        except (
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as api_error:
            error = True
            self.error_to_strings("%s" % api_error)
            self._connection = None
        except Exception as api_error:
            error = True
            _LOGGER.warning(
                "OpenMediaVault %s unexpected error during connect: %s",
                self._host,
                api_error,
            )
        else:
            if self.connection_error_reported:
                _LOGGER.warning("OpenMediaVault %s reconnected", self._host)
                self.connection_error_reported = False
            else:
                _LOGGER.debug("OpenMediaVault %s connected", self._host)

            self._connected = True
            self._reconnected = True
            self.lock.release()
            for cookie in self._connection.cookies:
                self._cookie_jar.set_cookie(cookie)

            save_cookies(self._cookie_jar_file, self._cookie_jar)

        # Socket errors
        if error:
            try:
                errorcode = response.status_code
            except Exception:
                errorcode = "no_respose"

            if errorcode == 200:
                errorcode = "cannot_connect"

            _LOGGER.warning(
                "OpenMediaVault %s connection error: %s", self._host, errorcode
            )

            error_code = errorcode
            self.error = error_code
            self._connected = False
            self.disconnect("connect")
            self.lock.release()

        return self._connected

    # ---------------------------
    #   error_to_strings
    # ---------------------------
    def error_to_strings(self, error=""):
        """Translate error output to error string."""
        self.error = "cannot_connect"
        if "Incorrect username or password" in error:
            self.error = "wrong_login"

        if "certificate verify failed" in error:
            self.error = "ssl_verify_failed"

    # ---------------------------
    #   connected
    # ---------------------------
    def connected(self) -> bool:
        """Return connected boolean."""
        return self._connected

    # ---------------------------
    #   query
    # ---------------------------
    def query(
        self,
        service: str,
        method: str,
        params: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> Any | None:
        """Retrieve data from OMV."""
        params = {} if params is None else params
        options = {"updatelastaccess": True} if options is None else options

        for attempt in range(2):
            if not self.connection_check():
                return None

            session_expired = False
            with self.lock:
                try:
                    _LOGGER.debug(
                        "OpenMediaVault %s query: %s, %s, %s, %s",
                        self._host,
                        service,
                        method,
                        params,
                        options,
                    )
                    response = self._connection.post(
                        self._resource,
                        data=json.dumps(
                            {
                                "service": service,
                                "method": method,
                                "params": params,
                                "options": options,
                            }
                        ),
                        verify=self._ssl_verify,
                    )
                    if response.status_code != 200:
                        self.error = response.status_code
                        self._connected = False
                        _LOGGER.warning(
                            "OpenMediaVault %s unable to fetch data (%s)",
                            self._host,
                            response.status_code,
                        )
                        return None

                    data = response.json()
                    _LOGGER.debug(
                        "OpenMediaVault %s query response: %s", self._host, data
                    )
                except (
                    requests.exceptions.RequestException,
                    json.decoder.JSONDecodeError,
                ) as api_error:
                    _LOGGER.warning(
                        "OpenMediaVault %s unable to fetch data", self._host
                    )
                    self.disconnect("query", api_error)
                    return None
                except Exception as api_error:
                    self.disconnect("query", api_error)
                    return None

                if not isinstance(data, dict):
                    self.error = "invalid_response"
                    _LOGGER.warning(
                        "OpenMediaVault %s returned an invalid response", self._host
                    )
                    return None

                api_error = data.get("error")
                if api_error is None:
                    self.error = None
                    return data.get("response")

                if not isinstance(api_error, dict):
                    self.error = "invalid_response"
                    _LOGGER.warning(
                        "OpenMediaVault %s returned an invalid API error", self._host
                    )
                    return None

                error_message = str(api_error.get("message", "Unknown API error"))
                error_code = api_error.get("code", "api_error")
                session_expired = error_code in (5001, 5002) or error_message in (
                    "Session not authenticated.",
                    "Session expired.",
                )
                if session_expired:
                    _LOGGER.debug("OpenMediaVault %s session expired", self._host)
                    self.error = 5001
                else:
                    self.error = error_code
                    _LOGGER.warning(
                        "OpenMediaVault %s API error in %s.%s: %s",
                        self._host,
                        service,
                        method,
                        error_message,
                    )
                    return None

            if session_expired and attempt == 0 and self.connect():
                continue
            return None

        return None
