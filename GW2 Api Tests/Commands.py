import requests, json
import pandas as pd
from io import StringIO

def Load(object):
    pd.json_normalize(object)
    