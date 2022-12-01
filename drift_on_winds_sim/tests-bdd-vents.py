import numpy as np
from matplotlib import pyplot as plt

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

def get_wind(conn, lvl = 10, t=1569072):

    wind = [[(0, 0)]*73]*144
    
    sqlu = "select lon, lat, u from uwind where level="+str(lvl)+" and t="+str(t)
    sqlv = "select lon, lat, v from vwind where level="+str(lvl)+" and t="+str(t)
    cur = conn.cursor()
    data = cur.execute(sqlu)
    for x in data:
        wind[int(x[0]/2.5)][int((x[1]+90)/2.5)] = [x[2], 0]

    data = cur.execute(sqlv)
    for x in data:
        wind[int(x[0]/2.5)][int((x[1]+90)/2.5)][1] = x[2]

    return wind





if __name__ == "__main__":


    conn = create_connection("wind.db")
    w = get_wind(conn)
    w2 = get_wind(conn, 70)
    print(w)

    plt.figure(1)
    for lon in range(144):
        for lat in range(73):
            u = w[lon][lat][0]
            v = w[lon][lat][1]
            plt.plot([lon, lon+u/50.],[lat, lat+v/50.], color="blue")

            u = w2[lon][lat][0]
            v = w2[lon][lat][1]
            plt.plot([lon, lon+u/50.],[lat, lat+v/50.], color="red")
    plt.show()
