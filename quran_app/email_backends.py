import socket
import smtplib

from django.core.mail.backends.smtp import EmailBackend


def _connect_ipv4(host, port, timeout):
    """Connect to host:port over IPv4, trying every A record in order.

    Returns the first socket that connects successfully. If every
    address fails, the last OSError is re-raised. Every socket created
    during a failed attempt is closed before moving on.
    """
    infos = socket.getaddrinfo(
        host, port, socket.AF_INET, socket.SOCK_STREAM
    )
    last_error = None
    for family, socktype, proto, _, sockaddr in infos:
        sock = None
        try:
            sock = socket.socket(family, socktype, proto)
            if timeout is not None:
                sock.settimeout(timeout)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            if sock is not None:
                sock.close()
    if last_error is not None:
        raise last_error
    raise OSError(f"getaddrinfo returned no IPv4 addresses for {host!r}")


class IPv4SMTP(smtplib.SMTP):
    """smtplib.SMTP that only connects over IPv4."""

    def _get_socket(self, host, port, timeout):
        return _connect_ipv4(host, port, timeout)


class IPv4SMTP_SSL(smtplib.SMTP_SSL):
    """smtplib.SMTP_SSL that only connects over IPv4 (for EMAIL_USE_SSL)."""

    def _get_socket(self, host, port, timeout):
        new_socket = _connect_ipv4(host, port, timeout)
        try:
            return self.context.wrap_socket(
                new_socket, server_hostname=self._host
            )
        except Exception:
            new_socket.close()
            raise


class IPv4EmailBackend(EmailBackend):
    """Django SMTP backend that forces IPv4 connections."""

    @property
    def connection_class(self):
        return IPv4SMTP_SSL if self.use_ssl else IPv4SMTP