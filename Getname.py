import requests
import json

"""
A bunch of functions returning data from common APIs
"""


def get_json(amount):
    request_html = "https://uinames.com/api/?ext&amount={}&region=poland"
    resp = requests.get(request_html.format(amount))
    r = json.loads(resp.text)
    return r


def json_to_person(amount):
    list_of_person = []
    r = get_json(amount)
    for i in r:
        print(str(len(i['surname'])) + ' ' + i['surname'])
        if len(i['surname']) < 3 or len(i['name']) < 3:
            print('XD')
            continue
        m_tuple = (i['name'], i['surname'])
        list_of_person.append(m_tuple)
    return list_of_person


def get_company():
    resp = requests.get('https://api.namefake.com/english-united-states', verify=False)
    return resp.json()


def get_address():
    resp = requests.get('https://randomuser.me/api/')
    return json.loads(resp.text)['results'][0]


def get_weirdo_name():
    resp = requests.get('https://api.whatdoestrumpthink.com/api/v1/quotes/random')
    return resp.json()['message']
