import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import yaml
import json

req.packages.urllib3.disable_warnings()

COIN_BLOCK_INFO_PATH = "coin_block_info"

def get_block_info(block_id, coin_wallet_cmd, nethash_block):

    try:
        process = subprocess.Popen("{} getblockhash {}".format(coin_wallet_cmd, block_id), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        output, error = process.communicate()
        block_hash = output.decode().strip()

        process = subprocess.Popen("{} getblock {}".format(coin_wallet_cmd, block_hash), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        output, error = process.communicate()
        block_info = json.loads(output.decode().strip())

        print("Nethash_block = {}".format(nethash_block))
        process = subprocess.Popen("{} getnetworkhashps {} {}".format(coin_wallet_cmd, nethash_block, block_id), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        output, error = process.communicate()
        nethash = output.decode().strip()

        block_info['nethash'] = nethash

    except Exception as e:
        print("GET Request Exception: {}".format(e))
        return None
    return block_info

def df_init(block_id, attribute, coin_wallet_cmd, nethash_block, fname):
    block_info = get_block_info(block_id, coin_wallet_cmd, nethash_block)
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

    sleep_interval = float(sys.argv[4])


    for coin in coin_collection:
        if coin_dict[coin]["explorer_type"] == "wallet":
            coin_wallet_cmd = coin_dict[coin]["cmd"]
            block_attribute = coin_dict[coin]["attribute"]
            nethash_block = coin_dict[coin]["nethash_block"]
            print(coin_wallet_cmd)
            print(block_attribute)

            process = subprocess.Popen("{} getblockcount".format(coin_wallet_cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            output, error = process.communicate()
            recent_block_id = int(output.decode().strip())

            print(recent_block_id)


            fname = os.path.join(COIN_BLOCK_INFO_PATH, coin+"_block_info.csv")

            if sys.argv[1] == "init":
                df_init(recent_block_id, block_attribute, coin_wallet_cmd, nethash_block, fname)

            if sys.argv[1] == "update":

            #     # Initialize it if Block File Doesn't Exist
                if not os.path.isfile(fname):
                    df_init(recent_block_id, block_attribute, coin_wallet_cmd, nethash_block, fname)

                # Update Part
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

                    block_info = get_block_info(recent_block_id, coin_wallet_cmd, nethash_block)
                    if not block_info:
                        time.sleep(sleep_interval)
                        continue

                    try:
                        refined_block_info = dict((key, block_info[key])
                                                  for key in block_attribute)
                    except Exception as e:
                        print("Extract Block Info Exception: {}".format(e))
                        recent_block_id -= 1
                        count += 1
                        continue

                    print("Retrieve Coin [{}] Block Info Successful. Height = {}".format(coin, refined_block_info["height"]))
                    print("")

                    for key in refined_block_info.keys():
                        # print("{}: {}".format(key, refined_block_info[key]))
                        df.loc[row, key] = refined_block_info[key]

                    recent_block_id -= 1
                    count += 1
                    time.sleep(sleep_interval)
                    df.sort_values(by="height", ascending=False)\
                      .head(2000)\
                      .to_csv(fname, index=False)

main()
