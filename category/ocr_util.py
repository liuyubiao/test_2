import requests
import json

ocr_url = 'http://127.0.0.1:5032/ocrReocg3'

def getOCR(imagePaths):
    payload = {
        "data": json.dumps(imagePaths)
    }
    merge = requests.post(url='%s' % (ocr_url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return json.loads(merge.text)