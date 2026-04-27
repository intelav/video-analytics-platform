from scapy.all import sniff

def process(pkt):
    print("GOOSE Packet Captured:", pkt.summary())

print("Listening for GOOSE packets...")

sniff(
    filter="ether proto 0x88b8",
    prn=process,
    store=0
)