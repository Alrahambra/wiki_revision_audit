#!/usr/bin/python3
from functions.wrevdit_functions import *
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Audits Wikipedia articles. Example: ./wrevdit.py https://en.wikipedia.org/wiki/Gomenasai_(t.A.T.u_song)",
        argument_default=argparse.SUPPRESS)

    parser.add_argument('initial_url', metavar='initial_url', type=str,
                        nargs=1, help="Article's URL.")

    args = parser.parse_args()
    urldata = parse_url(args.initial_url[0])
    print(parse_edit(get_json(urldata), urldata))
