import subprocess
# subprocess.run(['C:/Program Files (x86)/teraterm/ttermpro', '/C=3', '/BAUD=115200'])
# https://the.earth.li/~sgtatham/putty/0.63/htmldoc/Chapter3.html
subprocess.run(['putty', '-serial', 'COM3', '-sercfg', '115200,N'])