import time
import re
import timeago
import requests
from iota import Iota, Transaction, TransactionHash, Bundle, convert_value_to_standard_unit
from flask import url_for, flash
from datetime import datetime
from app.config import FULLNODE

DEPTH = 3

units = ['i', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi']

api = Iota(FULLNODE)

def get_convert(value):
    unit = units[int((len(str(abs(value)))-1) / 3)]
    if unit == 'i':
        convert = value
    else:
        convert = convert_value_to_standard_unit(str(value)+' i',unit)
    return [convert, unit]

def get_price(value):
    price = requests.get('https://min-api.cryptocompare.com/data/price?fsym=IOT&tsyms=USD').json()['USD']
    convert = get_convert(value)
    return [convert[0], convert[1], price*value/1000000, price]

def calculate_time(timestamp):
    return timeago.format(datetime.fromtimestamp(timestamp), datetime.now())

def confirmation(hash):
    return api.get_latest_inclusion(hashes=hash)['states']

def search_hash(type, hash):
    result = None

    if type == "tag" or type == "search":
        try:
            result = api.find_transactions(tags=[hash])

            if result['hashes'][0]:
                return "tag", result['hashes']
        except BaseException as e:
            result = e

    if type == "address" or type =="search":
        try:
            result = api.find_transactions(addresses=[hash])
            if result['hashes'][0]:
                balance = get_price(api.get_balances([hash])['balances'][0])
                tx = api.get_trytes(result['hashes'])['trytes']
                for num in range(len(tx)):
                    tx[num] = Transaction.from_tryte_string(tx[num])
                confirm = confirmation([element.hash for element in tx])
                for t in tx:
                    t.is_confirmed = confirm[t.hash]
                    t.timestamp = calculate_time(t.attachment_timestamp/1000)
                    t.value = get_convert(t.value)
                tx = sorted(tx, key=lambda k: k.attachment_timestamp, reverse=True)
                results = {'balance':balance, 'transactions':tx}
                return "address", results
        except BaseException as e:
            result = e

    if type == "transaction" or type =="search":
        try:
            tx = api.get_trytes(hashes=[hash])
            result = Transaction.from_tryte_string(tx['trytes'][0])
            if result.hash != TransactionHash(b''):
                result.timestamp = calculate_time(result.attachment_timestamp/1000)
                result.is_confirmed = confirmation([result.hash])[result.hash]
                result.value = get_price(result.value)
                return "transaction", result
        except BaseException as e:
            result = e

    if type == "bundle" or type =="search":
        try:
            result = api.find_transactions(bundles=[hash])['hashes']
            if result[0]:
                results = Bundle.from_tryte_strings(api.get_trytes(result)['trytes'])
                if True in confirmation(result).values():
                    results.is_confirmed = True
                for result in results:
                    result.value = get_convert(result.value)
                newlis = sorted(results, key=lambda k: k.attachment_timestamp, reverse=True)
                size = newlis[0].last_index+1
                newlist = [newlis[i:i+size] for i  in range(0, len(newlis), size)]
                for x in newlist:
                    x[0].timestamp = calculate_time(x[0].attachment_timestamp/1000)
                return "bundle", newlist
        except BaseException as e:
            result = e

    return "error", str(result)
