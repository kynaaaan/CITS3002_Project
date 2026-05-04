"""
Data flow on send:

    app_send -> L4.send -> L3.send_down -> L2.send_down
              -> Interface.transmit -> Link.transmit
              -> peer L2.receive -> peer L3.receive
              -> (router) L2.send_down  /  (host) L4.receive
"""

from protocol import Frame, Segment, Packet


MAX_DATA: int = 500 # Maximum application data bytes per Layer 4 segment


class Interface:
    """
    A network interface bound to a single Link.

    A host owns one Interface, a router owns one per port.

    Parameters
    ----------
    name : str
        Human readable label, e.g. Interface 1.
    ip : str
        IPv4 address assigned to this interface.
    mac : str
        MAC address assigned to this interface.

    Attributes
    ----------
    name : str
    ip : str
    mac : str
    link : Link or None
        The link this interface is attached to. Set via the attach method.
    datalink : DataLinkLayer or None
        Back reference to the owning devices L2, set by the device at
        construction time. The Link uses it to deliver inbound
        frames.
    """

    def __init__(self, name: str, ip: str, mac: str):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.link: Link | None = None
        self.datalink: DataLinkLayer | None = None

    def attach(self, link: Link) -> None:
        """
        Bind this interface to a link.

        Parameters
        ----------
        link : Link
            The link object connecting this interface to a peer.
        """
        pass

    def transmit(self, frame: Frame) -> None:
        """
        Hand a frame to the attached link for delivery to the peer.

        Parameters
        ----------
        frame : Frame
            Fully formed Layer 2 frame to send.

        Notes
        -----
        Convenience wrapper around self.link.transmit(frame, self).
        """
        pass


class Link:
    """
    A link connecting exactly two Interfaces.

    Parameters
    ----------
    a : Interface
    b : Interface

    Attributes
    ----------
    a : Interface
    b : Interface
    """

    def __init__(self, a: Interface, b: Interface):
        self.a = a
        self.b = b

    def transmit(self, frame: Frame, from_iface: Interface) -> None:
        """
        Deliver a frame from one endpoint to the other.

        Parameters
        ----------
        frame : Frame
            The frame leaving from_iface.
        from_iface : Interface
            The sending interface; used to locate the peer endpoint.
        """
        pass


class DataLinkLayer:
    """
    Layer 2: framing, MAC addressing and local delivery.

    Parameters
    ----------
    device_name : str
        Owning devices name, used as a log prefix.
    interfaces : list of Interface
        All interfaces this layer manages (one for hosts, multiple for
        routers).
    arp_table : dict of str to str
        Static map next_hop_ip: mac used to resolve outgoing
        Layer 2 destination addresses.

    Attributes
    ----------
    device_name : str
    interfaces : list of Interface
    arp_table : dict of str to str
    network : NetworkLayer or None
        Back reference to the owning devices L3 set by the device.
    learned : dict of str to tuple of (str, str)
        MAC learning table populated on receive: src_mac:
        (iface_name, ...)}.
    """

    def __init__(self, device_name: str, interfaces: list[Interface],
                 arp_table: dict[str, str]):
        self.device_name = device_name
        self.interfaces = interfaces
        self.arp_table = arp_table
        self.network: "NetworkLayer | None" = None
        self.learned: dict[str, tuple[str, str]] = {}

    def send_down(self, packet: Packet, next_hop_ip: str,
                  iface: Interface) -> None:
        """
        Encapsulate a packet in a frame and transmit it.

        Called by NetworkLayer. Logs frame creation and the transmission event 
        then calls iface.transmit(frame).

        Parameters
        ----------
        packet : Packet
            The Layer 3 packet to send.
        next_hop_ip : str
            IP of the directly reachable next hop, used for the ARP
            lookup that supplies the destination MAC.
        iface : Interface
            Outgoing interface chosen by L3.

        """
        pass

    def receive(self, frame: Frame, iface: Interface) -> None:
        """
        Handle an inbound frame from a Link.

        Parameters
        ----------
        frame : Frame
            Frame delivered by the link.
        iface : Interface
            The interface the frame arrived on.
        """
        pass

    def _lookup_mac(self, next_hop_ip: str) -> str:
        """
        Resolve a next hop IP to a destination MAC.

        Parameters
        ----------
        next_hop_ip : str

        Returns
        -------
        str
            MAC address from arp_table.
        """
        pass

    def _learn(self, src_mac: str, iface: Interface) -> None:
        """
        Record a newly observed source MAC and emit a log line.

        Parameters
        ----------
        src_mac : str
        iface : Interface
            The interface the MAC was observed on.
        """
        pass


RouteEntry = tuple[str, int, str | None, str]
"""
tuple: A routing table entry of the form (network, prefix, next_hop_or_None, iface_name).

next hop is None for directly connected routes, in that case the
next hop is the destination IP itself.
"""


class NetworkLayer:
    """Layer 3: addressing, routing, TTL handling.

    Parameters
    ----------
    device_name : str
        Owning devices name, used as a log prefix.
    interfaces : list of Interface
        All interfaces this layer can route out of.
    routing_table : list of RouteEntry
        Longest prefix match routing table for this device.
    is_router : bool
        True for the router (forwards on receive, decrements TTL);
        False for hosts (delivers locally on receive).

    Attributes
    ----------
    device_name : str
    interfaces : list of Interface
    routing_table : list of RouteEntry
    is_router : bool
    transport : TransportLayer or None
        Back reference to L4. None on a router.
    datalink : DataLinkLayer or None
        Back reference to L2.
    """

    def __init__(self, device_name: str, interfaces: list[Interface], routing_table: list[RouteEntry], is_router: bool):
        self.device_name = device_name
        self.interfaces = interfaces
        self.routing_table = routing_table
        self.is_router = is_router
        self.transport: "TransportLayer | None" = None
        self.datalink: "DataLinkLayer | None" = None

    def send_down(self, segment: Segment, src_ip: str, dst_ip: str) -> None:
        """
        Encapsulate a segment in a packet and forward to L2.

        Parameters
        ----------
        segment : Segment
            The Layer 4 segment to send.
        src_ip : str
            Source IP for the packet header.
        dst_ip : str
            Destination IP for the packet header.

        Notes
        -----
        Called by TransportLayer on a host, and by
        receive method on a router when forwarding. Performs a routing
        lookup via _route, builds a Packet with
        ttl=DEFAULT_TTL (host) or the existing TTL (if router forward),
        and calls self.datalink.send_down(packet, next_hop, iface).
        """
        pass

    def receive(self, packet: Packet, iface: Interface) -> None:
        """
        Handle an inbound packet from L2.

        Parameters
        ----------
        packet : Packet
            Packet delivered by L2.
        iface : Interface
            Interface the underlying frame arrived on.
        """
        pass

    def _route(self, dst_ip: str) -> tuple[Interface, str]:
        """
        Look up the outgoing interface and next hop IP for dst_ip.

        Parameters
        ----------
        dst_ip : str

        Returns
        -------
        tuple of (Interface, str)
            The chosen outgoing interface and the next hop IP. For a
            directly connected destination the next hop is dst_ip.
        """
        pass

    def _is_local(self, dst_ip: str) -> bool:
        """
        Check whether dst_ip matches one of this devices interfaces.

        Parameters
        ----------
        dst_ip : str

        Returns
        -------
        bool
            True if the packet should be delivered locally.
        """
        pass


class TransportLayer:
    """
    Layer 4: ports, checksum, rdt2.2.

    Because the simulation runs synchronously, the senders
    send blocks while network.send_down propagates all the
    way to the receiver and the ACK propagates back through
    receive. On return, sender state has been updated.

    Parameters
    ----------
    device_name : str
        Owning devices name, used as a log prefix.
    network : NetworkLayer
        Layer 3 used for outbound segments.

    Attributes
    ----------
    device_name : str
    network : NetworkLayer
    _awaiting_ack : int or None
        Sequence number the sender is currently waiting on, or None.
    _last_ack_seq : int or None
        Sequence number of the most recent valid ACK received.
    _expected_seq : int
        Next data sequence number the receiver expects (0 or 1).
    _last_ack_sent : int or None
        Sequence number of the most recent ACK transmitted; resent on
        duplicate or corrupt incoming DATA.
    """

    def __init__(self, device_name: str, network: "NetworkLayer"):
        self.device_name = device_name
        self.network = network
        self._awaiting_ack: int | None = None
        self._last_ack_seq: int | None = None
        self._expected_seq: int = 0
        self._last_ack_sent: int | None = None

    def send(self, data: bytes, src_ip: str, dst_ip: str, src_port: int, dst_port: int) -> None:
        """
        Reliably deliver data to (dst_ip, dst_port).

        Parameters
        ----------
        data : bytes
            Application payload of arbitrary length.
        src_ip : str
        dst_ip : str
        src_port : int
        dst_port : int

        Notes
        -----
        Splits data into chunks of at most MAX_DATA bytes.
        For each chunk, builds a segment with the current
        alternating sequence number, computes the checksum, sets
        _awaiting_ack and calls network.send_down. After
        send_down returns, checks _last_ack_seq against the
        expected value: if matched, flips the sequence number and
        proceeds otherwise retransmits.
        """
        pass

    def receive(self, segment: Segment, src_ip: str, dst_ip: str) -> None:
        """
        Handle an inbound segment from L3.

        Parameters
        ----------
        segment : Segment
            Segment delivered by L3.
        src_ip : str
            Source IP from the enclosing packet header (used to address
            the ACK).
        dst_ip : str
            Destination IP from the enclosing packet header (used as
            the ACK source).
        """
        pass

    def _send_ack(self, seq: int, src_ip: str, dst_ip: str, src_port: int, dst_port: int) -> None:
        """
        Build and transmit an ACK segment with the given sequence.

        Parameters
        ----------
        seq : int
            Sequence number to acknowledge (0 or 1).
        src_ip, dst_ip : str
            IPs for the enclosing packet header (note that the source
            and destination are reversed relative to the segment
            being acknowledged).
        src_port, dst_port : int
            Ports for the ACK mirror the original segment.
        """
        pass

    def _deliver(self, data: bytes) -> None:
        """
        Deliver verified application data to the local application.

        Parameters
        ----------
        data : bytes
            Payload extracted from a valid DATA segment.
        """
        pass


class Host:
    """
    A host device with a full L2/L3/L4 stack and one interface.

    Parameters
    ----------
    name : str
        Display name, e.g. Host A.
    interface : Interface
        The single network interface owned by this host.
    arp_table : dict of str to str
    routing_table : list of RouteEntry
        Typically a single default route via the hosts gateway.

    Attributes
    ----------
    name : str
    interface : Interface
    datalink : DataLinkLayer
    network : NetworkLayer
    transport : TransportLayer
    """

    def __init__(self, name: str, interface: Interface, arp_table: dict[str, str], routing_table: list[RouteEntry]):

        self.name = name
        self.interface = interface
        self.datalink = DataLinkLayer(name, [interface], arp_table)
        self.network = NetworkLayer(name, [interface], routing_table,
                                    is_router=False)
        self.transport = TransportLayer(name, self.network)
        interface.datalink = self.datalink
        self.datalink.network = self.network
        self.network.datalink = self.datalink
        self.network.transport = self.transport

    def app_send(self, data: bytes, dst_ip: str, dst_port: int,
                 src_port: int = 5000) -> None:
        """
        Send application layer data to a remote host.

        Parameters
        ----------
        data : bytes
            Message bytes to deliver.
        dst_ip : str
            Destination host IP.
        dst_port : int
            Destination application port.
        src_port : int, optional
            Source port to use, by default 5000.
        """
        pass


class Router:
    """
    A router device with L2 and L3 only and multiple interfaces.

    Parameters
    ----------
    name : str
        Display name, e.g. Router R1.
    interfaces : list of Interface
        All interfaces owned by this router.
    arp_table : dict of str to str
        Combined ARP table covering next hops on all interfaces.
    routing_table : list of RouteEntry

    Attributes
    ----------
    name : str
    interfaces : list of Interface
    datalink : DataLinkLayer
    network : NetworkLayer
    """

    def __init__(self, name: str, interfaces: list[Interface], arp_table: dict[str, str], routing_table: list[RouteEntry]):
        self.name = name
        self.interfaces = interfaces
        self.datalink = DataLinkLayer(name, interfaces, arp_table)
        self.network = NetworkLayer(name, interfaces, routing_table,
                                    is_router=True)
        
        for iface in interfaces:
            iface.datalink = self.datalink
        self.datalink.network = self.network
        self.network.datalink = self.datalink
