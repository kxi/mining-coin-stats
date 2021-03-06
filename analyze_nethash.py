import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials

COIN_NETHASH_INFO_PATH = "coin_nethash_info"
COIN_BLOCK_INFO_PATH = "coin_block_info"

def connect_to_gs():
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('key3.json', scope)
    gc = gspread.authorize(creds)
    wks = gc.open_by_url("https://docs.google.com/spreadsheets/d/12G_XdpgLKY_nb3zYI1BWfncjMJBcqVROkHoJcXO-JcE").worksheet("Coin Profit")
    return wks

def get_gs_coin_list(wks):
	gs_coin_list = wks.col_values(1)
	return gs_coin_list


def main():

    with open("coin_specs.yaml", 'r') as f:
        coin_dict = yaml.load(f)

    print(coin_dict.keys())

    if sys.argv[1] == "all":
        coin_collection = coin_dict.keys()
    elif sys.argv[1] in coin_dict.keys():
        print("Just One Coin: [{}]".format(sys.argv[1]))
        coin_collection = sys.argv[1].split()
    else:
        print("No Such Coin: [{}]".format(sys.argv[1]))

    wks = connect_to_gs()
    gs_coin_list = get_gs_coin_list(wks)

    for coin in coin_collection:

        if coin_dict[coin]['enabled'] == "no":
            continue

        coin_gs_row = gs_coin_list.index(coin) + 1
        dt_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if coin_dict[coin]["explorer_type"] == "Iquidus":
            fname = os.path.join(COIN_NETHASH_INFO_PATH, coin+"_nethash_info.csv")
            df = pd.read_csv(fname)
            nethash_latest = int(df['nethash'][0])

        if coin_dict[coin]["explorer_type"] == "UExplorer":
            fname = os.path.join(COIN_BLOCK_INFO_PATH, coin+"_block_info.csv")
            df = pd.read_csv(fname)
            nethash_latest = int(df['Network'][0])

        if coin_dict[coin]["explorer_type"] == "wallet":
            fname = os.path.join(COIN_BLOCK_INFO_PATH, coin+"_block_info.csv")
            df = pd.read_csv(fname)
            nethash_latest = int(df['nethash'][0])

        print("Analyzing Coin [{}]".format(coin))

        print("Coin [{}] Nethash is {}".format(coin, nethash_latest))

        wks.update_acell('L'+str(coin_gs_row), nethash_latest)
        wks.update_acell('V'+str(coin_gs_row), dt_now)

main()
