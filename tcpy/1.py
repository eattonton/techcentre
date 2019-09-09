# -*- coding: utf-8 -*-
import os, sys
sys.path.append('./tcpy')
import json

if __name__ == '__main__':
    arr1=[{"2019-08-05":8},{"2019-08-06":9}]
    for item1 in arr1:
        print(list(item1.values())[0])
        #print(item1)
