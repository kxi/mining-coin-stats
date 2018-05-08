import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import yaml

req.packages.urllib3.disable_warnings()

COIN_NETHASH_INFO_PATH = "coin_nethash_info"

def get_nethash_info(coin_explorer_url):
    r = req.get("{}api/getnetworkhashps".format(coin_explorer_url), verify=False)
    nethash = int(float(r.text))
    return nethash

def df_init(block_id, coin_explorer_url, fname):
    nethash_info = get_nethash_info(coin_explorer_url)
    labels = ['height','nethash']
    df = pd.DataFrame.from_records([(block_id, nethash_info)], columns=labels)
    df.to_csv(fname, index=False)


def main():

    with open("coin_specs.yaml", 'r') as f:
        coin_dict = yaml.load(f)

    print(coin_dict.keys())

    if sys.argv[2] == "all":
        coin_collection = coin_dict.keys()
    elif sys.argv[2] in coin_dict.keys():
        print("Just One Coin: [{}]".format(sys.argv[2]))
        coin_collection = sys.argv[2].split()
    else:
        print("No Such Coin: [{}]".format(sys.argv[2]))



    if sys.argv[1] == "init":
        for coin in coin_collection:
            coin_explorer_url = coin_dict[coin]["url"]
            print(coin_explorer_url)

            r = req.get("{}api/getblockcount".format(coin_explorer_url), verify=False)
            recent_block_id = int(r.text)

            fname = os.path.join(COIN_NETHASH_INFO_PATH, coin+"_nethash_info.csv")
            df_init(recent_block_id, coin_explorer_url, fname)


    if sys.argv[1] == "update":
        while True:
            for coin in coin_collection:

                coin_explorer_url = coin_dict[coin]["url"]
                print(coin_explorer_url)

                try:
                    r = req.get("{}api/getblockcount".format(coin_explorer_url), verify=False)
                    recent_block_id = int(r.text)
                    nethash_info = get_nethash_info(coin_explorer_url)
                except Exception as e:
                    print(e)
                    print("")
                    continue

                fname = os.path.join(COIN_NETHASH_INFO_PATH, coin+"_nethash_info.csv")
                
                if not os.path.isfile(fname):
                    df_init(recent_block_id, coin_explorer_url, fname)
                
                df = pd.read_csv(fname)
                row = df.size

                print("Coin [{}]: Block ID = {}, Nethash = {}".format(coin, recent_block_id, nethash_info))

                if recent_block_id in df["height"].tolist():
                    print("Coin [{}] Block Info Height Existed. Bypass".format(coin))
                    print("")
                    time.sleep(0.5)
                    continue

                labels = ['height','nethash']
                df2 = pd.DataFrame.from_records([(recent_block_id, nethash_info)], columns=labels)
                df=df.append(df2, ignore_index=True)

                df.sort_values(by="height", ascending=False)\
                  .head(2000)\
                  .to_csv(fname, index=False)

            break
main()
