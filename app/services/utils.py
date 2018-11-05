import time
import re
from iota import Iota, Transaction, Address, Fragment
from flask import url_for

FULLNODE = 'https://node.deviceproof.org:443'
DEPTH = 3

api = Iota(FULLNODE)

def retry_bundle(hash):
    tryte = api.get_trytes(hashes=[hash])['trytes'][0]
    tx = Transaction.from_tryte_string(tryte)

    charRe = re.compile(r'[^9.]')
    if charRe.search(str(tx.hash)) and tx.current_index == 0:
        if api.get_latest_inclusion([tx.hash])['states'][tx.hash]:
            return "Transaction is already confirmed."
        elif (round(time.time()) - tx.timestamp) < 300:
            try:
                result = api.promote_transaction(transaction=hash, depth=DEPTH)
                return "Transaction is promoted."
            except:
                result = api.replay_bundle(transaction=hash, depth=DEPTH)
                return "Transaction is reattached."
        else:
            result = api.replay_bundle(transaction=hash, depth=DEPTH)
            return "Transaction is reattached."
    else:
        return "Invalid transaction provided."

def track_bundle_loop(hash):
    all_tx = None
    try:
        all_tx = api.find_transactions(addresses=[Address(hash)])
        all_inclusion = api.get_latest_inclusion(all_tx['hashes'])
    except:
        return all_tx, 4
    tx_list = {key:val for key, val in all_inclusion['states'].items() if val == True}

    input = None
    ds = 0
    for tx_hash in tx_list:
        tx = Transaction.from_tryte_string(api.get_trytes([tx_hash])['trytes'][0])
        if tx.value < 0:
            input = tx
            ds += 1
            break

    if input is None:
        return hash, 1#"Address hasn't used yet."
    elif ds > 1:
        return hash, 2#"Address has been reused twice or more."

    while input.current_index != input.last_index:
        input = Transaction.from_tryte_string(api.get_trytes([input.trunk_transaction_hash])['trytes'][0])

    if input.signature_message_fragment != Fragment(b''):
        return input.address, 3#"Track failed."

    return input.address, 0

def track_bundle(hash):
    hash = Address(hash)
    address, state = track_bundle_loop(hash)
    while state == 0:
        address, state = track_bundle_loop(address)

    if state == 1:
        if address == hash:
            return str(address.with_valid_checksum()), "Original address hasn't used yet:"
        else:
            return str(address.with_valid_checksum()), "New address found:"

    elif state == 2:
        return None, "Tracked address has been reused twice or more."
    elif state == 3:
        return None, "Last address tracked didn't leave remainder address."
    else:
        return None, "Could not find any record in current epoch."
