# coding: utf-8

"""
DEPRECATED

use instead : cli.py
"""

from cli import *

if __name__ == "__main__":
    try:
        if sys.argv[2].endswith("2id"):
            action_align()
        elif sys.argv[2] == "marc2tables":
            action_marc2tables()
        elif sys.argv[2] == "ark2records":
            action_ark2records()
    except IndexError:
        print("\nParam --action is missing.\nAuthorized values : bib2id, aut2id, marc2tables, ark2records")    
    