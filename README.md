######  Retrieve Nethash Data for all coins. Sleep 1 sec after each iteration.
python run_nethash_dump.py all 1

python run_nethash_dump.py EXVO 1


######  Retrieve Last 50 Block Data for all coins. Sleep 0.2 sec after each iteration.
python check_block_info.py update all 50 0.2


######  Upload Block/Day and Diff to gspread
python analyze_block_info.py all


######  Upload Nethash and Diff to gspread
python analyze_nethash.py all






