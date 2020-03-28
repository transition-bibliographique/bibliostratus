# coding: utf-8

version = 1.29
lastupdate = "28/03/2020"
programID = "bibliostratus"


import codecs
import os
import json
import re
import tkinter as tk
import webbrowser
from tkinter import filedialog
from urllib import error, request

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

