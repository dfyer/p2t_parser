# -*- coding: utf-8 -*-

# PYTHON-3!!

import os
import sys
import unicodedata

path = "./"

for f in os.listdir(path):
    if f.endswith(".csv"):
        with open(f, "r") as raw:
            text = raw.read()
        with open("encoded/" + f, "w") as encoded:
            norm = unicodedata.normalize("NFC", text)
            encoded.write(norm)
