"""
dimensions:
	lon = 144 ;
	lat = 73 ;
	level = 17 ;

1569072

 level = 1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 
    30, 20, 10 ;

"""

levels = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10];
level_id = {level: id for id,level in enumerate(levels)}


import numpy as np
from matplotlib import pyplot as plt
from time import time

import math
import sqlite3
from sqlite3 import Error


# === database connexion code ===

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)

    except Error as e:
        print(e)

    cur = conn.cursor()
    cur.execute("pragma synchronous = off;")
    return conn

def get_wind(conn, timestamp = 1569072):
    """retourne toute les données de vents pour un timestamp"""

    wind = [[[[0, 0] for _ in range(73)] for _ in range(144)] for _ in range(17)]
    
    sqlu = "select level, lon, lat, u from uwind where t="+str(timestamp)
    sqlv = "select level, lon, lat, v from vwind where t="+str(timestamp)
    sql_test = "select level, lon, lat, v from vwind limit 200000"

    cur = conn.cursor()
    cur.execute(sql_test)

    counter = 0
    t0 = time()
    end = False
    while not end:
        x = cur.fetchone()
        end = (x == None)
        counter += 1
        if counter%10000 == 0:
            print(f"{counter}: avg time of {(time()-t0)/10000*1000}ms by row")
            t0 = time()
        #wind[level_id[x[0]]][int(x[1]/2.5)][int((x[2]+90)/2.5)][0] = x[3]

    data = cur.execute(sqlv)

    for x in data:
        wind[level_id[x[0]]][int(x[1]/2.5)][int((x[2]+90)/2.5)][1] = x[3]

    return wind




