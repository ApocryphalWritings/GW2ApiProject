#!/usr/bin/env python3

import requests
import json
from pprint import pprint
from datetime import datetime
from json import JSONEncoder
from argparse import ArgumentParser


class Gw2Gold(object):
    def __init__(self, value=None) -> None:
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

    def get_coins(self) -> tuple:
        """
        Returns the number of gold, silver, and copper as a tuple
        """
        silver = self.copper // 100
        gold = silver // 100
        silver = silver % 100
        copper = self.copper % 100
        return (gold, silver, copper)

    def __str__(self) -> str:
        gold, silver, copper = self.get_coins()
        if gold != 0:
            return '{:4d} gold, {:2d} silver, {:2d} copper'.format(
                gold, silver, copper
            )
        elif silver != 0:
            return '{:13d} silver, {:2d} copper'.format(silver, copper)
        else:
            return '{:24d} copper'.format(copper)

    def __repr__(self) -> str:
        return "Gw2Gold('" + str(self) + "')"


class Gw2Velocity(object):
    def __init__(self, buy, sell, supply, demand):
        self.buy = buy
        self.sell = sell
        self.supply = supply
        self.demand = demand

        VelCircs = None
        VelCircb = None
        TotalVel = None

        self.v1 = VelCircs
        self.v2 = VelCircb
        self.v3 = TotalVel

    def __str__(self) -> str:
        """
        First row is values for printing
        Second row is for json output
        """
        try:
            retval = '\n '
            VelCircs = self.supply / self.sell
            VelCircb = self.supply / self.buy
            retval += 'Buy velocity: {}, \n Sell velocity: {}, \n '.format(
                VelCircb, VelCircs
            )
            TVel = self.supply + self.demand
            Total = self.buy + self.sell
            retval += 'Total Velocity(buy and sell): {}'.format(TVel / Total)
            return retval
        except Exception as b:
            print('Supply or Demand is 0')
            pass

    def __repr__(self) -> str:
        return "Gw2Velocity('" + str(self) + "')"


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Gw2Gold):
            gold, silver, copper = o.get_coins()
            return {'Gold': gold, 'Silver': silver, 'Copper': copper}
        if isinstance(o, Gw2Velocity):
            return {
                'Buy Velocity:': o.v1,
                'Sell Velocity:': o.v2,
                'Total Velocity:': o.v3
            }
        return super(Encoder, self).default(o)


if __name__ == '__main__':
    parser = ArgumentParser(
        description=' '.join((
            'a program to manipulate the gw2tp API to discover',
            'information about items on the Guild Wars 2 Trading Post'
        ))
    )
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Operate in interactive mode')
    args = parser.parse_args()

    # item ids, name
    Names = requests.get(
        "http://api.gw2tp.com/1/bulk/items-names.json"
    ).json()
    # every item on the trading post right now
    Prices = requests.get(
        "http://api.gw2tp.com/1/bulk/items.json"
    ).json()
    NamesMapping = {
        k: v for k, v in Names['items']
    }

    print('Last updated:', datetime.fromtimestamp(Prices['updated'] / 1000))

    Items = dict()
    for item in Prices['items']:
        Items[item[0]] = {
            "Name": NamesMapping[item[0]],
            "Buy": Gw2Gold(item[1]),
            "Sell": Gw2Gold(item[2]),
            "Supply": item[3],
            "Demand": item[4],
            "Velocity": Gw2Velocity(item[1],
                                    item[2],
                                    item[3],
                                    item[4])
        }

    ExampleItems = {
        1: {
            "Name": "ItemName",
            "Buy": Gw2Gold(0),
            "Sell": Gw2Gold(3),
            "Supply": 10,
            "Demand": 30
        },
        2: {  # <----- the keys in the Items dictionary
            "Name": "Item2Name",  # are the Item ID from the API
            "Buy": Gw2Gold(3),
            "Sell": Gw2Gold(6),
            "Supply": 8,
            "Demand": 9
        }
    }

    if args.interactive:
        while itemid := input('Enter an item ID: '):  # noqa: E203,E701,E231,E225,E999,E501
            try:
                ThisItem = Items[int(itemid)]
                print(f'{ThisItem["Name"]} (id {itemid}):')
                print(
                    f'  Buying:  {ThisItem["Buy"]}',
                    f'({ThisItem["Demand"]} demand)'
                )
                print(
                    f'  Selling: {ThisItem["Sell"]}',
                    f'({ThisItem["Supply"]} supply)'
                )
                print(f' {ThisItem["Name"]} velocity is',
                      f'{ThisItem["Velocity"]})')
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

    with open('Output.json', mode='w+', encoding='utf-8') as outputfile:
        outputfile.write(json.dumps(Items, cls=Encoder))
