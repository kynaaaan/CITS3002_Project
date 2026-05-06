import struct
from dataclasses import dataclass

ETHERTYPE_IPV4 = 0x0800
PROTO_UDP = 17
TYPE_DATA = 0
TYPE_ACK = 1
DEFAULT_TTL = 100


@dataclass
class Frame:
    """
    Layer 2 frame.

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
        return (
            self._mac_to_bytes(self.dst_mac)
            + self._mac_to_bytes(self.src_mac)
            + struct.pack(">H", self.ethertype)
            + self.payload
        )

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
        dst_mac = cls._bytes_to_mac(raw[0:6])
        src_mac = cls._bytes_to_mac(raw[6:12])
        (ethertype,) = struct.unpack(">H", raw[12:14])
        payload = raw[14:]
        return cls(dst_mac, src_mac, ethertype, payload)

    @staticmethod
    def _mac_to_bytes(mac: str) -> bytes:
        """
        Convert a MAC string to 6 raw bytes.

        Parameters
        ----------
        mac : str
            MAC address in XX:XX:XX:XX:XX:XX form.

        Returns
        -------
        bytes
            Six byte representation.
        """
        return bytes.fromhex(mac.replace(":", ""))

    @staticmethod
    def _bytes_to_mac(raw: bytes) -> str:
        """
        Convert 6 raw bytes to a colon separated uppercase MAC string.

        Parameters
        ----------
        raw : bytes
            Six byte buffer.

        Returns
        -------
        str
            MAC address in XX:XX:XX:XX:XX:XX form.
        """
        return ":".join(f"{b:02X}" for b in raw)



@dataclass
class Packet:
    """
    Layer 3 packet.

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
        return (
            self._ip_to_bytes(self.src_ip)
            + self._ip_to_bytes(self.dst_ip)
            + struct.pack(">BBH", self.ttl, self.proto, self.total_length)
            + self.payload
        )

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
        src_ip = cls._bytes_to_ip(raw[0:4])
        dst_ip = cls._bytes_to_ip(raw[4:8])
        ttl, proto, total_length = struct.unpack(">BBH", raw[8:12])
        payload = raw[12:]
        return cls(src_ip, dst_ip, ttl, proto, total_length, payload)

    @staticmethod
    def _ip_to_bytes(ip: str) -> bytes:
        """
        Convert a dotted-quad IPv4 string to 4 raw bytes.

        Parameters
        ----------
        ip : str
            IPv4 address in dotted form.

        Returns
        -------
        bytes
            Four byte representation.
        """
        return bytes(int(octet) for octet in ip.split("."))

    @staticmethod
    def _bytes_to_ip(raw: bytes) -> str:
        """
        Convert 4 raw bytes to a dotted IPv4 string.

        Parameters
        ----------
        raw : bytes
            Four byte buffer.

        Returns
        -------
        str
            IPv4 address in dotted form.
        """
        return ".".join(str(b) for b in raw)

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

        Returns
        -------
        int
            The newly computed 16 bit checksum.
        """
        self.checksum = 0
        self.checksum = self._checksum(self.to_bytes())
        return self.checksum

    def verify(self) -> bool:
        """
        Check whether the stored checksum matches the segment contents.

        Returns
        -------
        bool
            True if the segment is intact, False if corrupted.
        """
        return self._checksum(self.to_bytes()) == 0

    def to_bytes(self) -> bytes:
        """Serialise the segment to its byte representation.

        Returns
        -------
        bytes
            src_port (2) + dst_port (2) + length (2) +
            checksum (2) + type (1) + seq (1) + data.
        """
        return (
            struct.pack(
                ">HHHHBB",
                self.src_port, self.dst_port,
                self.length, self.checksum,
                self.type, self.seq,
            )
            + self.data
        )

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
        (src_port, dst_port, length, checksum,
         type_, seq) = struct.unpack(">HHHHBB", raw[0:10])
        data = raw[10:]
        return cls(src_port, dst_port, length, checksum, type_, seq, data)

    @staticmethod
    def _checksum(data: bytes) -> int:
        """
        Compute the ones complement checksum.

        Parameters
        ----------
        data : bytes
            Byte buffer to checksum.

        Returns
        -------
        int
            16 bit checksum value.
        """
        if len(data) % 2:
            data += b"\x00"
        total = 0
        for i in range(0, len(data), 2):
            total += (data[i] << 8) | data[i + 1]
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)
        return (~total) & 0xFFFF
