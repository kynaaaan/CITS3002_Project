from dataclasses import dataclass

ETHERTYPE_IPV4 = 0x0800
PROTO_UDP = 17
TYPE_DATA = 0
TYPE_ACK = 1
DEFAULT_TTL = 100


@dataclass
class Frame:
    """
    Layer 2 (Ethernet-like) frame.

    Attributes
    ----------
    dst_mac : str
        Destination MAC address in XX:XX:XX:XX:XX:XX.
    src_mac : str
        Source MAC address in XX:XX:XX:XX:XX:XX.
    ethertype : int
        Two byte type field. ETHERTYPE_IPV4 for an IP payload.
    payload : bytes
        Serialised class Packet.
    """
    dst_mac: str
    src_mac: str
    ethertype: int
    payload: bytes

    def to_bytes(self) -> bytes:
        """
        Serialise the frame to its byte representation.

        Returns
        -------
        bytes
            Concatenation of dst_mac (6) + src_mac (6) +
            ethertype (2) + payload.
        """
        pass

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Frame":
        """
        Parse a frame from its byte representation.

        Parameters
        ----------
        raw : bytes
            Bytes beginning with a Layer 2 header.

        Returns
        -------
        Frame
            A new instance with payload set to the remaining bytes.
        """
        pass


@dataclass
class Packet:
    """
    Layer 3 (IP-like) packet.

    Attributes
    ----------
    src_ip : str
        Source IPv4 address in dotted form.
    dst_ip : str
        Destination IPv4.
    ttl : int
        Time to live. Decremented at each router the packet is
        dropped when TTL reaches zero.
    proto : int
        Upper layer protocol identifier (1 byte). PROTO_UDP 
        signals a UDP like segment payload.
    total_length : int
        Header (12 bytes) + payload size (2 bytes).
    payload : bytes
        Serialised class Segment.
    """
    src_ip: str
    dst_ip: str
    ttl: int
    proto: int
    total_length: int
    payload: bytes

    def to_bytes(self) -> bytes:
        """
        Serialise the packet to its byte representation.

        Returns
        -------
        bytes
            src_ip (4) + dst_ip (4) + ttl (1) + proto (1)
            + total_length (2) + payload
        """
        pass

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Packet":
        """
        Parse a packet from its byte representation.

        Parameters
        ----------
        raw : bytes
            Buffer beginning with a Layer 3 header.

        Returns
        -------
        Packet
            A new instance with payload set to the remaining bytes.
        """
        pass


@dataclass
class Segment:
    """Layer 4 segment.

    Attributes
    ----------
    src_port : int
        Source port.
    dst_port : int
        Destination port.
    length : int
        Header + data length.
    checksum : int
        16 bit CRC field. Populated by method compute_checksum.
    type : int
        TYPE_DATA (0) or TYPE_ACK (1).
    seq : int
        Alternating bit sequence number, 0 or 1.
    data : bytes
        Application payload. Empty for ACK segments.
    """
    src_port: int
    dst_port: int
    length: int
    checksum: int
    type: int
    seq: int
    data: bytes

    def compute_checksum(self) -> int:
        """
        Compute the 16 bit ones complement checksum over the segment.

        The checksum field itself is treated as zero while the value is
        being computed, the result is then stored back into the checksum
        attribute.

        Returns
        -------
        int
            The newly computed 16 bit checksum.
        """
        pass

    def verify(self) -> bool:
        """
        Check whether the stored checksum matches the segment contents.

        Returns
        -------
        bool
            True if the segment is intact, False if corrupted.
        """
        pass

    def to_bytes(self) -> bytes:
        """Serialise the segment to its byte representation.

        Returns
        -------
        bytes
            src_port (2) + dst_port (2) + length (2) +
            checksum (2) + type (1) + seq (1) + data.
        """
        pass

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Segment":
        """
        Parse a segment from its byte representation.

        Parameters
        ----------
        raw : bytes
            Buffer beginning with a Layer 4 header.

        Returns
        -------
        Segment
            A new instance with data set to the remaining bytes.
        """
        pass
