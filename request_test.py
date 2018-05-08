import subprocess
import sys
import os
import time
from datetime import datetime
import requests as req
import pandas as pd
import yaml

req.packages.urllib3.disable_warnings()

def main():
    r = req.get("https://explorer.folm.io/api/chart/stat", verify=False)
    block_info = r.json()
    print(block_info[0]['Difficulty'])
    print(block_info[0]['Block'])
    print(block_info[0]['Network'])
    print(block_info[0]['Time'])
main()
