# coding: utf-8

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

version = 1.28
lastupdate = "16/01/2019"
programID = "bibliostratus"
