from helper import *
import json
from web3 import Web3, HTTPProvider, WebsocketProvider
import sys
import os
import time
import random
import hashlib
from operator import attrgetter

import pandas as pd
import numpy_financial as npf
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

#!pip install yfinance
import yfinance as yf
import datetime as dt

verbose = True
stats_verbose = True
gas_verbose = False
graph_verbose = False
total_gas = 0

# kept in client memory
ciphertexts = {}

# kept in server memory
addr2keys = {}
addr2name = {}
# experiment parameters
Total_investment = 10000
Tranche_1_investment = Total_investment * 0.6
Tranche_2_investment = Total_investment * 0.2
Tranche_3_investment = Total_investment * 0.2
no_borrowers_1 = Tranche_1_investment / 100
no_borrowers_2 = Tranche_2_investment / 100
no_borrowers_3 = Tranche_3_investment / 100
borrowers_1 = [100] * int(no_borrowers_1)
borrowers_2 = [100] * int(no_borrowers_2)
borrowers_3 = [100] * int(no_borrowers_3)
payment_1 = 0
payment_2 = 0
payment_3 = 0


contract_path = "./build/contracts/MortgageBackedSecurities.json"
contractAddress = ""

investor_num = 100
borrower_num = 100

truffleFile = json.load(open(contract_path))
abi = truffleFile["abi"]


truffle_url = "http://127.0.0.1:8545"
w3 = Web3(HTTPProvider(truffle_url))

if w3.isConnected():
    print("Web3 Connected")
else:
    sys.exit("Couldn't connect to the blockchain via web3")

w3.eth.defaultAccount = w3.eth.accounts[0]

for i in range(1, Total_investment + 1):
    addr2name[w3.eth.accounts[i]] = str(i)


if not contractAddress:
    contractAddress = deploy_contract(w3, contract_path)


mbs = w3.eth.contract(address=contractAddress, abi=abi)
for i in range(1, investor_num + 1):
    addr = w3.eth.accounts[i]
    addr2keys[addr] = generate_key()
    inn = addr2keys[addr].public_key.format(True)
    tx = mbs.functions.stakeTokens(addr, inn).transact()

for i in range(1, borrower_num + 1):
    addr = w3.eth.accounts[i]
    addr2keys[addr] = generate_key()
    brr = addr2keys[addr].public_key.format(True)
    tx = mbs.functions.loanTokens(addr, inn).transact()


def tranche_1(int):
    coupon = 0.0335
    term = 60
    # payments
    periods = range(1, term + 1)
    interest_payment = npf.ipmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    principal_payment = npf.ppmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    return interest_payment + principal_payment


for i in range(len(borrowers_1)):
    py = tranche_1(borrowers_1[i])
    payment = mbs.functions.unstakeTokens()
    payment_1 = np.add(payment_1, payment)


def tranche_2(int):
    coupon = 0.035
    term = 60
    # payments
    periods = range(1, term + 1)
    interest_payment = npf.ipmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    principal_payment = npf.ppmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    return interest_payment + principal_payment


for i in range(len(borrowers_2)):
    py = tranche_2(borrowers_2[i])
    payment = mbs.functions.unstakeTokens()
    payment_2 = np.add(payment_2, payment)


def tranche_3(int):
    coupon = 0.037
    term = 60
    # payments
    periods = range(1, term + 1)
    interest_payment = npf.ipmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    principal_payment = npf.ppmt(rate=coupon / 12, per=periods, nper=term, pv=-int)
    return interest_payment + principal_payment


for i in range(len(borrowers_3)):
    py = tranche_3(borrowers_3[i])
    payment = mbs.functions.unstakeTokens()
    payment_3 = np.add(payment_3, payment)

total_payment_1 = 0
for i in range(len(payment_1)):
    total_payment_1 = total_payment_1 + payment_1[i]
total_payment_1

total_payment_2 = 0
for i in range(len(payment_2)):
    total_payment_2 = total_payment_2 + payment_2[i]
total_payment_2

total_payment_3 = 0
for i in range(len(payment_3)):
    total_payment_3 = total_payment_3 + payment_3[i]
total_payment_3


def returns(i, t):
    r = t / i - 1
    return r


tranche_1_return = returns(Tranche_1_investment, total_payment_1)
tranche_2_return = returns(Tranche_2_investment, total_payment_2)
tranche_3_return = returns(Tranche_3_investment, total_payment_3)

start = dt.datetime(2016, 1, 1)
end = dt.datetime(2021, 12, 31)

eth = yf.download("ETH-USD", start, end)


start_price = eth["Close"][0]
end_price = eth["Close"][1513]

dollar_investment_1 = start_price * Tranche_1_investment
dollar_payment_1 = end_price * total_payment_1
dollar_investment_2 = start_price * Tranche_2_investment
dollar_payment_2 = end_price * total_payment_2
dollar_investment_3 = start_price * Tranche_3_investment
dollar_payment_3 = end_price * total_payment_3

dollar_tranche_1_return = returns(dollar_investment_1, dollar_payment_1)
dollar_tranche_2_return = returns(dollar_investment_2, dollar_payment_2)
dollar_tranche_3_return = returns(dollar_investment_3, dollar_payment_3)
