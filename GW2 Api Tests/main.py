import requests, json
from pprint import pprint
from datetime import datetime


class Gw2Gold(object):
    def __init__(self, value = None) -> None:
        if type(value) == int:
            self.copper = value
        elif type(value) == str:
            stuff = value.split(',')
            if len(stuff) == 3:
                gold = int(stuff[0].split()[0])
                silver = int(stuff[1].split()[0])
                copper = int(stuff[2].split()[0])
            elif len(stuff) == 2:
                gold = 0
                silver = int(stuff[0].split()[0])
                copper = int(stuff[1].split()[0])
            else:
                gold = 0
                silver = 0
                copper = int(stuff[0].split()[0])
            self.copper = copper + 100 * silver + 10000 * gold
        else:
            self.copper = 0

    def __str__(self) -> str:
        silver = self.copper // 100
        gold = silver // 100
        silver = silver % 100
        copper = self.copper % 100
        if gold != 0:
            return '{:4d} gold, {:2d} silver, {:2d} copper'.format(gold, silver, copper)
        elif silver != 0:
            return '{:13d} silver, {:2d} copper'.format(silver, copper)
        else:
            return '{:24d} copper'.format(copper)

    def __repr__(self) -> str:
        return "Gw2Gold('" + str(self) + "')"

if __name__ == '__main__':
    #Item ids, name
    Names = requests.get("http://api.gw2tp.com/1/bulk/items-names.json").json()
    #Every item on the trading post right now 
    Prices = requests.get("http://api.gw2tp.com/1/bulk/items.json").json()

    NamesMapping = {
        k: v for k, v in Names['items']
    }

    print('Last updated:',
        datetime.fromtimestamp(
            Prices['updated'] / 1000
        )
    )
 
    Items = dict()
    for item in Prices['items']:
        Items[item[0]] = {
            "Name": NamesMapping[item[0]],
            "Buy": Gw2Gold(item[1]),
            "Sell": Gw2Gold(item[2]),
            "Supply": item[3],
            "Demand": item[4]
        }

    ExampleItems = {
        1: {
            "Name": "ItemName",
            "Buy": Gw2Gold(0),
            "Sell": Gw2Gold(3),
            "Supply": 10,
            "Demand": 30
        },
        2: {  # <----- the keys in the Items dictionary are the Item ID from the API
            "Name": "Item2Name",
            "Buy": Gw2Gold(3),
            "Sell": Gw2Gold(6),
            "Supply": 8,
            "Demand": 9
        }
    }

    while itemid:= input('Enter an item ID: '):
        try:
            ThisItem = Items[int(itemid)]
            print(f'{ThisItem["Name"]} (id {itemid}):')
            print(f'  Buying:  {ThisItem["Buy"]} ({ThisItem["Demand"]} demand)')
            print(f'  Selling: {ThisItem["Sell"]} ({ThisItem["Supply"]} supply)')
        except KeyError as e:
            print(f'No item {itemid}')
            pass
        except ValueError as e:
            print(f'Bad input type, {itemid} is not integer')
            pass
        except Exception as e:
            print('Unknown exception:')
            print(e)
            pass
    print('Good bye')
    with open('Output.json', mode='w', encoding='utf-8') as outputfile:
        json.dump(Items, outputfile)

    exit()