import requests, json



Names = requests.get("http://api.gw2tp.com/1/bulk/items-names.json")

with open('Inames.json', 'w') as outfile:
    json.dump(Names.json(), outfile, sort_keys=True)
    

Prices = requests.get("http://api.gw2tp.com/1/bulk/items.json")

with open('Iprices.json', 'w') as out:
    json.dump(Prices.json(), out, sort_keys=True)
    
with open('Inames.json') as f:
    data = json.load(f)
    
