from scapy.all import sniff

def process(pkt):
    print("GOOSE Packet:", pkt.summary())

sniff(filter="ether proto 0x88b8", prn=process, store=0)