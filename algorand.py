# -*- coding: utf-8 -*-
"""
@author: gianc
"""
#install microsoft C++ dev tools
#pip install --upgrade pip
#pip install py-algorand-sdk
#https://developer.algorand.org/docs/sdks/python/
#https://developer.algorand.org/tutorials/creating-python-transaction-purestake-api/
#https://developer.purestake.io/signup  ##create your API KEY for interacting with algorand blockchain. No need locally algorand full node

#configure the wallet for sending your token to your subscribers
#need privaty key for signing the transaction in algorand blockchain testnet
my_address = "MY PUBLIC ADDRESS"
private_key = "MY PRIVATE KEY"
API_KEY = 'MY PURESTAKE ACCESS KEY'
passphrase = 'MY PASSPHRASE'

import json
import time
import base64
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk.future.transaction import AssetTransferTxn


# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print('Waiting for confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print('Transaction confirmed in round', txinfo.get('confirmed-round'))
    return txinfo


def send_token_to_subscribers(address):
    # Setup HTTP client w/guest key provided by PureStake
    algod_token = API_KEY
    algod_address = 'https://testnet-algorand.api.purestake.io/ps2'
    purestake_token = {'X-Api-key': algod_token}
    
    # Initalize throw-away account for this example - check that is has funds before running script
    mnemonic_phrase = passphrase;
    account_private_key = mnemonic.to_private_key(mnemonic_phrase)
    account_public_key = mnemonic.to_public_key(mnemonic_phrase)
    
    algodclient = algod.AlgodClient(algod_token, algod_address, headers=purestake_token)
    
    # get suggested parameters from Algod
    params = algodclient.suggested_params()
   
    existing_account = account_public_key
    send_to_address = address
    asset_id = 00000000  ###Insert your minted token: this is mine https://testnet.algoexplorer.io/asset/67045293
    # Create and sign transaction
    #tx = transaction.PaymentTxn(existing_account, fee, first_valid_round, last_valid_round, gh, send_to_address, send_amount, flat_fee=True)
    tx = AssetTransferTxn(sender=existing_account, sp=params, receiver=send_to_address, amt=1, index=asset_id)
    signed_tx = tx.sign(account_private_key)
    
    try:
        tx_confirm = algodclient.send_transaction(signed_tx)
        print('Transaction sent with ID', signed_tx.transaction.get_txid())
        wait_for_confirmation(algodclient, txid=signed_tx.transaction.get_txid())
        return True
    except Exception as e:
        print(e)
    
