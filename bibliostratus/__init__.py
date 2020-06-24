# coding: utf-8

version = 1.31
lastupdate = "24/06/2020"
programID = "bibliostratus"


import codecs
import os
import json
import re
import smc.bibencodings
import tkinter as tk
import webbrowser
from tkinter import filedialog
from urllib import error, request
import pymarc

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

