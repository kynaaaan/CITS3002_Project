import sys
from typing import List, Tuple

from config import (
    HOST_A_NAME, HOST_A_IFACE_NAME, HOST_A_IP, HOST_A_MAC,
    R1_NAME,
    R1_IF1_NAME, R1_IF1_IP, R1_IF1_MAC,
    R1_IF2_NAME, R1_IF2_IP, R1_IF2_MAC,
    HOST_B_NAME, HOST_B_IFACE_NAME, HOST_B_IP, HOST_B_MAC,
    ARP_TABLE_HOST_A, ARP_TABLE_R1, ARP_TABLE_HOST_B,
    ROUTING_TABLE_HOST_A, ROUTING_TABLE_R1, ROUTING_TABLE_HOST_B,
    APP_SRC_PORT, APP_DST_PORT,
)
from devices import Host, Router, Interface, Link


def build_topology() -> Tuple[Host, Router, Host]:
    """
    Construct and wire up the simulator topology.

    Returns
    -------
    tuple of (Host, Router, Host)
        (host_a, router, host_b) with both point-to-point links
        attached to the relevant interfaces.

    Notes
    -----
    Two links are created: Host A <-> Router R1 (Interface 1) and
    Router R1 (Interface 2) <-> Host B. Each interface is then
    explicitly attached to its link so that the link can route inbound
    frames into the correct device's data link layer.
    """
    a_iface = Interface(HOST_A_IFACE_NAME, HOST_A_IP, HOST_A_MAC)
    r1_if1 = Interface(R1_IF1_NAME, R1_IF1_IP, R1_IF1_MAC)
    r1_if2 = Interface(R1_IF2_NAME, R1_IF2_IP, R1_IF2_MAC)
    b_iface = Interface(HOST_B_IFACE_NAME, HOST_B_IP, HOST_B_MAC)

    host_a = Host(HOST_A_NAME, a_iface, ARP_TABLE_HOST_A, ROUTING_TABLE_HOST_A)
    router = Router(R1_NAME, [r1_if1, r1_if2], ARP_TABLE_R1, ROUTING_TABLE_R1)
    host_b = Host(HOST_B_NAME, b_iface, ARP_TABLE_HOST_B, ROUTING_TABLE_HOST_B)

    link_ar = Link(a_iface, r1_if1)
    a_iface.attach(link_ar)
    r1_if1.attach(link_ar)

    link_rb = Link(r1_if2, b_iface)
    r1_if2.attach(link_rb)
    b_iface.attach(link_rb)

    return host_a, router, host_b


def parse_message_size(argv: List[str]) -> int:
    """
    Validate and parse the CLI message size argument.

    Parameters
    ----------
    argv : list of str
        Process arg.

    Returns
    -------
    int
        Number of bytes to send.

    Raises
    ------
    SystemExit
        If the argument is missing or not a non negative integer.
    """
    if len(argv) != 2:
        print("Usage: python main.py <message_size_in_bytes>", file=sys.stderr)
        raise SystemExit(2)
    try:
        size = int(argv[1])
    except ValueError:
        print(f"Invalid size: {argv[1]!r}", file=sys.stderr)
        raise SystemExit(2)
    if size < 0:
        print("Message size must be non negative", file=sys.stderr)
        raise SystemExit(2)
    return size


def main(argv: List[str]) -> int:
    """
    Build the topology and send a single message from Host A to Host B.

    Parameters
    ----------
    argv : list of str
        sys.argv for the running process.

    Returns
    -------
    int
        Process exit status.
    """
    size = parse_message_size(argv)
    host_a, _router, _host_b = build_topology()

    message = b"x" * size
    host_a.app_send(message, HOST_B_IP, APP_DST_PORT, src_port=APP_SRC_PORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
