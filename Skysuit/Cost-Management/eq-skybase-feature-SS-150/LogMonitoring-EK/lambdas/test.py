import os
import json
from collections import namedtuple



listnew = "a,b,c,d,e".split(",")
listold = "d,e,f,g,h".split(",")
# listold = "".split(",")

print (listnew)
print (listold)

BucketInfo =   namedtuple('BucketInfo', 'addthese deletethese')

def get_diff(listold_: list , listnew_: list) -> (list, list):
    createthese = []
    deletethese = []

    for elem in listnew_:
        if elem not in listold_: createthese.append(elem)

    for elem in listold_:
        if elem not in listnew_: deletethese.append(elem)
    
    binfo = BucketInfo(createthese, deletethese)

    return binfo #createthese, deletethese

b1 = get_diff(listold, listnew)

print (f"new items {b1.addthese}" )
print (f"delete these items {b1.deletethese}" )









