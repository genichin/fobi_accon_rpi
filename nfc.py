import time
from pynfc import Nfc, Desfire, Timeout
import fba_common

def nfcscan_start(msg_q) :    
    while True :
        try :
            n = Nfc("pn532_i2c:/dev/i2c-1")    
            for target in n.poll():
                #print(target)
                print(target.uid)
                msg_q.put((fba_common.EVENT_NFC_DETECTED, target.uid))
                time.sleep(3)
        except Exception as e :
            print(e)
            pass
        
