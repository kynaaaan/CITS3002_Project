# CITS3002 Project

A simulation of a three layer network stack (Data Link, Network, Transport) delivering data from Host A to Host B through Router R1. Only the Python standard library is used.

## Running

```
python main.py <message_size_in_bytes>
```

Example: `python main.py 100` sends a 100 byte application message from Host A to Host B and prints the log of the round trip (DATA frames out, ACK frames back).

Messages longer than 500 bytes are automatically split into multiple Layer 4 segments and sent sequentially using rdt2.2.

## File layout

| File          | Purpose                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| `main.py`     | Entry point. Parses the message, builds the topology and then sends the message. |
| `protocol.py` | Classes for the three layers: `Frame` (L2), `Packet` (L3), `Segment` (L4). |
| `devices.py`  | Layer classes (`DataLinkLayer`, `NetworkLayer`, `TransportLayer`) plus the `Interface`, `Link`, `Host` and `Router` wrappers. |
| `config.py`   | Fixed parameters for IPs, MACs, ARP tables, routing tables.                |

## Implementation summary

### Layer 2: Data Link (`DataLinkLayer`)

- **Framing:** wraps the L3 packet in a `Frame` with source/destination MAC and an EtherType of `0x0800` which is IPv4.
- **MAC addressing:** each device holds a static ARP table mapping next hop IPs to MAC addresses. The destination MAC is resolved on every send.
- **MAC learning:** THE source MAC of every inbound frame is recorded against the interface it arrived on.
- **Delivery:** valid IPv4 frames are decapsulated and the packet is passed up to L3.

### Layer 3: Network (`NetworkLayer`)

- **Encapsulation:** wraps the L4 segment in a `Packet`.
- **Routing:** longest prefix match lookup against a routing table. For a directly connected route the next hop is set to the destination IP itself.
- **Forwarding (router only):** decrements TTL on inbound packets and drops the packet if TTL reaches 0,otherwise reroutes and hands the packet back to L2.
- **Local delivery (host only):** if the destination IP matches one of the interfaces of the host, the payload is passed up to L4.

### Layer 4: Transport (`TransportLayer`)

- **Segmentation:** application data is split into chunks of up to `MAX_DATA = 500` bytes with one `Segment` per chunk.
- **Ports & length:** each segment carries source/destination ports and the total segment length.
- **Checksum:** a 16-bit internet checksum is computed on send and verified on receive. Corrupted segments are discarded and the previous ACK is sent again.
- **rdt2.2:** the sender attaches sequence number 0/1, blocks until the matching ACK returns, then flips for the next chunk. On a duplicate or corrupted DATA segment the receiver sends its last ACK, on a bad ACK the sender retransmits the current segment.
- **ACKs:** every valid DATA segment is acknowledged with an `ACK` segment carrying the same sequence number addressed back to the sender.

## Data flow on send

```
app_send -> L4.send -> L3.send_down -> L2.send_down
         -> Interface.transmit -> Link.transmit
         -> peer L2.receive -> peer L3.receive
         -> (router) L2.send_down  /  (host) L4.receive
```

Because the simulation is synchronous, `network.send_down` does not return on the sender until the packet has propagated through R1 to Host B and the ACK has propagated all the way back at which point the senders `_last_ack_seq` has already been updated and the rdt2.2 loop can decide whether to advance or retransmit.

## Assumptions

- No packet loss or frame corruption.
- All transmissions are deterministic.
- ARP and routing tables are populated in `config.py`. Dynamic discovery is limited.
