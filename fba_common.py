import struct

EVENT_BLE_DETECTED = 1
EVENT_NFC_DETECTED = 2

def returnstringpacket(pkt):
    myString = ""
    for c in pkt:
        myString +=  "%02x" % c
    return myString 