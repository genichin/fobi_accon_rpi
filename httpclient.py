import http.client
import json
import datetime


def send(uid, ctype):
    try:
        conn = http.client.HTTPConnection('127.0.0.1', 8080)
        headers = {'Content-type': 'application/json'}

        foo = {'device_id': '00010','time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'uid': uid, 'type': ctype}
        json_data = json.dumps(foo)

        conn.request('POST', '/checkin', json_data, headers)

        response = conn.getresponse()
        print(response.read().decode())
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    send('11111')