# coding: utf-8

version = 1.33
version_suffix = ""   # contenu : "RC1", "RC2", "RC3", etc.
lastupdate = "25/11/2021"
programID = "bibliostratus"


import codecs
import os
import json
import re
import smc.bibencodings
#from pkg_resources import py2_warn
import tkinter as tk
import webbrowser
from tkinter import filedialog
from urllib import error, request
import pymarc
import ssl

from joblib import Parallel, delayed
import multiprocessing

from unidecode import unidecode

import main
import marc2tables
import bib2id
import aut2id
import ark2records
import funcs
import forms

import mapping_number_letters
import sru
import udecode

