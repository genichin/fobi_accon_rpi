import sys
import queue
import subprocess
import fba_common

def nfcscan_start(msg_q) :
    while True :
        p = subprocess.Popen(['stdbuf', '-o0', 'nfc-poll'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True)
                        
        while p.poll() == None:
            out = p.stdout.readline()
            if out.find('UID (') != -1 :
                uid = out[out.find('): ')+3:].replace("\n", "")
                uid = uid.replace(" ", "")
                msg_q.put((fba_common.EVENT_NFC_DETECTED, uid))
                print(uid)

if __name__ == '__main__':
    message_queue = queue.Queue()
    nfcscan_start(message_queue)
