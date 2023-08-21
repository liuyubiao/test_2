import requests
import json
import threading

ocr_url = 'http://127.0.0.1:5039/WordSize'

def sendWordSize(barcode,ocrResults):
    payload = {
        "barCode": barcode,
        "ocrResults": json.dumps(ocrResults)
    }
    try:
        merge = requests.post(url='%s' % (ocr_url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    except:
        pass
    return


def threadingSend(barcode,ocrResults):
    task = threading.Thread(target=sendWordSize,args=(barcode,ocrResults))
    task.start()

    return