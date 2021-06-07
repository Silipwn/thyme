# License: BSD-3-Clause
# Finis coronat opus
# Run at your own peril. @silipwn
# Filename: auto-window.py
# Description: X11 only minimal python script for getting window names and stats
# Author: silipwn (contact at as-hw.in)
# Date: 2021-06-07T17:33:50+0530
# Last Modification Date: 2021-06-07T17:50:35+0530
#           By: silipwn
# URL:
# Junk place
# from IPython import embed; embed()

import subprocess
import re


# Source: https://stackoverflow.com/questions/3983946/get-active-window-title-in-x
def get_active_window_title():
    root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                            stdout=subprocess.PIPE)
    stdout, stderr = root.communicate()

    m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
    if m != None:
        window_id = m.group(1)
        window = subprocess.Popen(['xprop', '-id', window_id, 'WM_NAME'],
                                  stdout=subprocess.PIPE)
        stdout, stderr = window.communicate()
    else:
        return None

    match = re.match(b"WM_NAME\(\w+\) = (?P<name>.+)$", stdout)
    if match != None:
        return match.group("name").decode('utf-8').replace('"','')

    return None


def get_all_titles():
    titles = []
    root = subprocess.Popen(['xprop', '-root', '_NET_CLIENT_LIST'],
                            stdout=subprocess.PIPE)
    stdout, stderr = root.communicate()

    clients = stdout.decode('utf-8').split('#')[1]
    clients = re.sub(r"\W+|_", " ", clients).strip()

    client_list = clients.split()
    for i in range(0, len(client_list)):
        window = subprocess.Popen(['xprop', '-id', client_list[i], 'WM_NAME'],
                                  stdout=subprocess.PIPE)
        stdout, stderr = window.communicate()

        if stdout:
            output = stdout.decode('utf-8').split('=')[1]
            name = output.replace('"','').strip()
            titles.append(name)
        else:
            print('Error occured')
            raise SystemError

    return titles

if __name__ == "__main__":
    titles=get_all_titles()
    print('Priting a list of windows')
    for index in titles:
        print(index)
    print('The active window is :{0}'.format(get_active_window_title()))
