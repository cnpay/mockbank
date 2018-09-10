import requests
import time
import datetime
import hashlib
import collections

def sign(payload):
    ordered_payload = collections.OrderedDict(sorted(payload.items()))
    pre_md5 = "&".join(['%s=%s' % (key, value) for (key, value) in ordered_payload.items()])
    pre_md5 += "&paySecret=5ade00245e0c44bd9e712767b0cb9d18"
    md5 = hashlib.md5()
    md5.update(pre_md5.encode("UTF-8"))
    result = md5.hexdigest().upper()
    return result

payload = { \
    "payKey":"0478179bd18f47afb29f5689c8850a81", \
    "orderPrice":"0.01", \
    "outTradeNo":str(int(time.time()*1000)), \
    "productType":"50000103", \
    "orderTime":f"{datetime.datetime.now():%Y%m%d%H%M%S}", \
    "productName":"水杯", \
    "orderIp":"127.0.0.1", \
    "bankCode":"ICBC", \
    "bankAccountType":"PRIVATE_DEBIT_ACCOUNT", \
    "returnUrl":"http://127.0.0.1:8888/returnUrl", \
    "notifyUrl":"http://127.0.0.1:8888/notifyUrl", \
    "remark":"python之b2c支付备注", \
}

payload["sign"]=str(sign(payload))

result = requests.post("http://127.0.0.1:8080/gateway/b2cPay/initPay",data=payload)
print(result.text)