import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import yaml

COIN_BLOCK_INFO_PATH = "coin_block_info"

def get_block_info(block_id, coin_explorer_url):
    try:
        r = req.get("{}api/getblockhash?index={}".format(coin_explorer_url, block_id))
        block_hash = r.text

        r = req.get("{}api/getblock?hash={}".format(coin_explorer_url, block_hash))
        block_info = r.json()
    except Exception as e:
        print("GET Request Exception: {}".format(e))
        return None
    return block_info

def df_init(block_id, attribute, coin_explorer_url, fname):
    block_info = get_block_info(block_id, coin_explorer_url)
    refined_block_info = dict((key, block_info[key])
                              for key in attribute)
    # print(refined_block_info)
    df = pd.DataFrame(refined_block_info, index=[0])
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

    for coin in coin_collection:

        coin_explorer_url = coin_dict[coin]["url"]
        block_attribute = coin_dict[coin]["attribute"]

        print(coin_explorer_url)
        print(block_attribute)

        r = req.get("{}api/getblockcount".format(coin_explorer_url))
        recent_block_id = int(r.text)
        print(recent_block_id)


        fname = os.path.join(COIN_BLOCK_INFO_PATH, coin+"_block_info.csv")

        if sys.argv[1] == "init":
            df_init(recent_block_id, block_attribute, coin_explorer_url, fname)

        if sys.argv[1] == "update":

            last_n_block = int(sys.argv[3])


            count = 0

            while count < last_n_block:

                df = pd.read_csv(fname)
                row = df.size

                print("Coin [{}]: Check Block, ID = {}".format(coin, recent_block_id))

                if recent_block_id in df["height"].tolist():
                    print("Coin [{}] Block Info Height Existed. Bypass".format(coin))
                    print("")
                    recent_block_id -= 1
                    count += 1
                    continue

                block_info = get_block_info(recent_block_id, coin_explorer_url)
                if not block_info:
                    time.sleep(1)
                    continue

                refined_block_info = dict((key, block_info[key])
                                          for key in block_attribute)

                print("Retrieve Coin [{}] Block Info Successful. Height = {}".format(coin, refined_block_info["height"]))
                print("")

                for key in refined_block_info.keys():
                    # print("{}: {}".format(key, refined_block_info[key]))
                    df.loc[row, key] = refined_block_info[key]

                recent_block_id -= 1
                count += 1
                time.sleep(0.2)
                df.sort_values(by="height", ascending=False)\
                  .head(2000)\
                  .to_csv(fname, index=False)

main()
