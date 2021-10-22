import struct
import queue
import time
import bluetooth._bluetooth as bluez
import fba_common

ble_lists = []

def parse_adv_report(pkt) :
    packet = {}
    rssi = pkt[-1]
    if rssi > 127 :
        rssi = rssi - 256
    #print("RSSI =", rssi)
    packet["rssi"] = rssi
    num_reports = pkt[4]
    #print("num_reports =", num_reports)
    report_pkt_offset = 5
    packet["reports"] = []
    for i in range(0, num_reports):
        # build the return string
        report = {}
        report["preamble"] = pkt[report_pkt_offset:report_pkt_offset+3]
        #print("Preamble :", returnstringpacket(report["preamble"]))
        report_pkt_offset += 3
        report["accaddr"] = pkt[report_pkt_offset:report_pkt_offset+4]
        #print("Access Address :", returnstringpacket(report["accaddr"]))
        report_pkt_offset += 4
        pdu_length = pkt[report_pkt_offset+1]
        #print("PDU Type : %02X" % pkt[report_pkt_offset], ", PDU Length :", pdu_length)
        report_pkt_offset += 2
        report["data"] = []
        while pdu_length > 0 :
            data_length = pkt[report_pkt_offset]
            data_type = pkt[report_pkt_offset + 1]
            report["data"].append([data_type, pkt[report_pkt_offset+2:report_pkt_offset+data_length+1]])
            #print("  %i"%data_length, ",%i :" %data_type, returnstringpacket(pkt[report_pkt_offset+2:report_pkt_offset+data_length+1]))
            report_pkt_offset += (data_length + 1)
            pdu_length -= (data_length + 1)
        packet["reports"].append(report)
    return packet

def blescan_start(msg_q) :
    try:
        sock = bluez.hci_open_dev(0)
        print ("ble thread started")

    except:
        print ("error accessing bluetooth device...")
        return

    bluez.hci_send_cmd(sock, 0x08, 0x000C, struct.pack("<BB", 0x01, 0x00))  #Enable LE Scan
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    while True:
        pkt = sock.recv(255)        
        #print(returnstringpacket(pkt))
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        #print(ptype, event, plen)
        if event == 0x3E: #LE_META_EVENT
            subevent = pkt[3]
            if subevent == 0x02 : #EVT_LE_ADVERTISING_REPORT
                packet = parse_adv_report(pkt)
                #print(packet)
                for report in packet["reports"] :
                    found = False
                    for data in report['data'] :
                        if data[0] == 3 and data[1][0] == 0xB2 and data[1][1] == 0xD1:
                            found = True
                    if found == True :
                        for data in report['data'] :
                            if data[0] == 9:
                                #print (packet["rssi"], data[1])                                
                                exist = False
                                for item in ble_lists:
                                    if item["value"] == data[1] :
                                        now = time.time()
                                        if now - item["time"] > 3 :
                                            item["time"] = now
                                            item["rssi"] = [packet["rssi"]]
                                            msg_q.put((fba_common.EVENT_BLE_DETECTED, item))
                                        else :
                                            item["rssi"].append(packet["rssi"])
                                            if len(item["rssi"]) > 100 :
                                                del item["rssi"][0]
                                        #print("time :", now - item["time"])
                                        item["time"] = now
                                        exist = True                                        
                                if exist == False :
                                    ble_lists.append({"time":time.time(),"rssi":[packet["rssi"]],"value":data[1]})
                                    msg_q.put((fba_common.EVENT_BLE_DETECTED, ble_lists[-1]))
            else :
                print("subevent is not 0x02 : %02X"%subevent)    
        else :
            print("event is not 0x3E : %02X"%event)

if __name__ == '__main__':
    message_queue = queue.Queue()
    blescan_start(message_queue)
