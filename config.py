

# Subnets 
NETWORK_1_ADDR = "10.0.1.0"
NETWORK_2_ADDR = "10.0.2.0"
SUBNET_PREFIX = 24

# Host A 
HOST_A_NAME = "Host A"
HOST_A_IFACE_NAME = "eth0"
HOST_A_IP = "10.0.1.10"
HOST_A_MAC = "AA:AA:AA:AA:AA:AA"

# Router R1 
R1_NAME = "Router R1"
R1_IF1_NAME = "Interface 1"
R1_IF1_IP = "10.0.1.1"
R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"
R1_IF2_NAME = "Interface 2"
R1_IF2_IP = "10.0.2.1"
R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"

# Host B 
HOST_B_NAME = "Host B"
HOST_B_IFACE_NAME = "eth0"
HOST_B_IP = "10.0.2.20"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

# ARP tables: {next_hop_ip: mac} 
ARP_TABLE_HOST_A: dict[str, str] = {
    R1_IF1_IP: R1_IF1_MAC,      # gateway
}

ARP_TABLE_R1: dict[str, str] = {
    HOST_A_IP: HOST_A_MAC, # neighbour on Network 1
    HOST_B_IP: HOST_B_MAC, # neighbour on Network 2
}

ARP_TABLE_HOST_B: dict[str, str] = {
    R1_IF2_IP: R1_IF2_MAC, # gateway
}

# Routing tables: [(network, prefix, next_hop_or_None, iface_name),] 
ROUTING_TABLE_HOST_A: list[tuple[str, int, str | None, str]] = [
    (NETWORK_1_ADDR, SUBNET_PREFIX, None, HOST_A_IFACE_NAME), # connected
    ("0.0.0.0", 0, R1_IF1_IP, HOST_A_IFACE_NAME), # default
]

ROUTING_TABLE_R1: list[tuple[str, int, str | None, str]] = [
    (NETWORK_1_ADDR, SUBNET_PREFIX, None, R1_IF1_NAME),
    (NETWORK_2_ADDR, SUBNET_PREFIX, None, R1_IF2_NAME),
]

ROUTING_TABLE_HOST_B: list[tuple[str, int, str | None, str]] = [
    (NETWORK_2_ADDR, SUBNET_PREFIX, None, HOST_B_IFACE_NAME), # connected
    ("0.0.0.0", 0, R1_IF2_IP, HOST_B_IFACE_NAME), # default
]

APP_SRC_PORT = 5000
APP_DST_PORT = 80
