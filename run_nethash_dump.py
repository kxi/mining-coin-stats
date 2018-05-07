import subprocess
import sys
import time
from datetime import datetime

def main():
    coin = sys.argv[1]
    interval_sec = float(sys.argv[2])
    timeout_sec = 180
    sleep_sec = interval_sec - timeout_sec

    while 1:
        print("###############################################################")
        print("Start Dump Nethash @ {}".format((str(datetime.now()))))
        now = time.time()

        try:
#            process = subprocess.call("python check_network_hash.py update {}".format(coin, interval_sec), stderr=subprocess.STDOUT, timeout = timeout_sec)

            system_command=subprocess.Popen("python check_network_hash.py update {}".format(coin, interval_sec), shell=True, stdout=subprocess.PIPE)
            stdout, stderr = system_command.communicate()
            print(stdout)

        except Exception as e:
            print(e)

        print("Finish Dump Nethash @ {}".format((str(datetime.now()))))
        print("****** It Takes {0:.1f} Second to Finish Dump Nethash! ******".format(time.time() - now))

        print("Start Sleep")
        print("###############################################################")
        print("")

        time.sleep(interval_sec)

main()
