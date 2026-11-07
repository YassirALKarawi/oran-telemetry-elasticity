"""Inspect build tools and exercise a local native SCTP association."""
import json
import platform
import shutil
import socket
from pathlib import Path


def receive(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("peer closed during payload exchange")
        data.extend(chunk)
    return bytes(data)


def check_transport():
    stage = "socket"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP) as listener:
            listener.settimeout(2)
            stage = "bind/listen"
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP) as client:
                client.settimeout(2)
                stage = "connect/accept"
                client.connect(listener.getsockname())
                peer, _ = listener.accept()
                with peer:
                    peer.settimeout(2)
                    stage = "payload exchange"
                    payload = b"transport-preflight"
                    client.sendall(payload)
                    peer.sendall(receive(peer, len(payload)))
                    if receive(client, len(payload)) != payload:
                        raise ValueError("payload mismatch")
        return {"round_trip": True}
    except (AttributeError, OSError, ValueError) as error:
        return {"round_trip": False, "stage": stage, "errno": getattr(error, "errno", None),
                "error": str(error)}


if __name__ == "__main__":
    tools = {name: shutil.which(name) for name in ("git", "cmake", "make", "g++", "swig",
                                                   "bison", "flex", "pkg-config")}
    header = Path("/usr/include/netinet/sctp.h").is_file()
    print(json.dumps(dict(system=platform.platform(), tools=tools, sctp_header=header,
                          build_prerequisites_present=bool(all(tools.values()) and header),
                          native_ipv4_sctp=check_transport()), indent=2))
