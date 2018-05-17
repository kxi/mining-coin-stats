import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import yaml

req.packages.urllib3.disable_warnings()

COIN_BLOCK_INFO_PATH = "coin_block_info"

def get_block_info(coin_explorer_url):
    try:
        r = req.get("{}api/chart/stat".format(coin_explorer_url), verify=False)
        block_info = r.json()
    except Exception as e:
        print("GET Request Exception: {}".format(e))
        return None
    return block_info

def df_init(attribute, coin_explorer_url, fname):
    block_info = get_block_info(coin_explorer_url)[0]
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

        if coin_dict[coin]["enabled"] == "no":
            continue

        if coin_dict[coin]["explorer_type"] == "UExplorer":
            coin_explorer_url = coin_dict[coin]["url"]
            block_attribute = coin_dict[coin]["attribute"]

            print(coin_explorer_url)
            print(block_attribute)

            fname = os.path.join(COIN_BLOCK_INFO_PATH, coin+"_block_info.csv")

            if sys.argv[1] == "init":
                df_init(block_attribute, coin_explorer_url, fname)

            if sys.argv[1] == "update":

                # Initialize it if Block File Doesn't Exist
                if not os.path.isfile(fname):
                    df_init(block_attribute, coin_explorer_url, fname)

                count = 0

                df = pd.read_csv(fname)
                row = df.size

                # print("Coin [{}]: Check Block, ID = {}".format(coin, recent_block_id))

                block_info = get_block_info(coin_explorer_url)
                if not block_info:
                    print("Block Info is Empty, Please Check")
                    continue

                for i in range(len(block_info)):
                    recent_block_id = block_info[i]['Block']

                    if recent_block_id in df["Block"].tolist():
                        print("Coin [{}] Block Info Height Existed. Bypass".format(coin))
                        print("")
                        continue

                    try:
                        refined_block_info = dict((key, block_info[i][key])
                                                  for key in block_attribute)
                    except Exception as e:
                        print("Extract Block Info Exception: {}".format(e))
                        continue

                    print("Retrieve Coin [{}] Block Info Successful. Height = {}".format(coin, refined_block_info["Block"]))
                    print("")

                    for key in refined_block_info.keys():
                        # print("{}: {}".format(key, refined_block_info[key]))
                        df.loc[row, key] = refined_block_info[key]

                    row += 1

                df = df

                df.sort_values(by="Block", ascending=False)\
                  .head(2000)\
                  .to_csv(fname, index=False)

main()
