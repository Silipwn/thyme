# License: AGPL-3.0-or-later
# Finis coronat opus
# Run at your own peril. @silipwn
# Filename: auto-window.py
# Description: X11 only minimal python script for getting window names and stats
# Author: silipwn (contact at as-hw.in)
# Created: 2021-06-07T17:33:50+0530
# Last-Updated: 2021-06-13T10:27:35+0530
#           By: silipwn
# URL:https://github.com/Silipwn/thyme
#

# Change Log:
#
# Junk place
# from IPython import embed; embed()
import subprocess
import re
import argparse
import time
import json
import signal
import logging


def signal_handler(sig, frame):
    logging.warning('Ctrl+C detected, exiting program!')
    raise SystemExit


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
        return match.group("name").decode('utf-8').replace('"', '')

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
            name = output.replace('"', '').strip()
            titles.append(name)
        else:
            logging.error('Error occured while parsing value')
            raise SystemError

    return titles


def capture(output_file):
    # Get time
    json_data = {}
    with open(output_file, 'a+') as json_file:
        current_time = time.localtime()
        timestamp = time.strftime("%FT%T%z", current_time)
        # json_data[timestamp] = {}
        # titles = get_all_titles()
        # json_data[timestamp]['Applications'] = titles
        # print('Printing a list of windows')
        # for index in titles:
        #     print(index)
        # print('The active window is :{0}'.format(get_active_window_title()))
        json_data[timestamp] = get_active_window_title()
        json.dump(json_data, json_file)
        json_file.write('\n')
        logging.debug('Dumped values into {0} for time {1}'.format(
            output_file, timestamp))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    generate = subparsers.add_parser('generate', help='Generate help')
    generate.add_argument(
        "sample_time",
        help="Sampling time (seconds) for the script (Default: 10s)",
        type=int,
        default=10)
    generate.add_argument("-o",
                          "--output",
                          action="store",
                          type=str,
                          help="Output file for JSON")
    generate.add_argument(
        "-v",
        "--verbosity",
        action="store",
        type=str,
        help=
        "Verbosity for the framework (https://docs.python.org/3/howto/logging.html#logging-levels)",
        default='INFO')

    stats = subparsers.add_parser('stats', help='Stats help')
    stats.add_argument("-g",
                       "--graph",
                       action="store",
                       type=str,
                       default='bar',
                       help="Graph type from JSON (Default: Bar graph)")
    stats.add_argument(
        "-v",
        "--verbosity",
        action="store",
        type=str,
        help=
        "Verbosity for the framework (https://docs.python.org/3/howto/logging.html#logging-levels)",
        default='INFO')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=args.verbosity)
    if args.output:
        output_file = args.output
    else:
        output_file = 'thyme.json'
    signal.signal(signal.SIGINT, signal_handler)
    starttime = time.time()
    while True:
        try:
            capture(output_file)
            time.sleep(
                int(args.sample_time) -
                ((time.time() - starttime) % int(args.sample_time)))
        except KeyboardInterrupt:
            logging.warning('Exiting')
            raise SystemExit
