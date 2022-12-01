import math
import sqlite3
from sqlite3 import Error


# === table creation code ===

sql_create_vwind_table = """ CREATE TABLE IF NOT EXISTS vwind (
                                        id integer PRIMARY KEY,
                                        level real,
                                        lat real,
                                        lon real,
                                        t integer,
                                        v real

                                    ); """
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
    
def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_entry(conn, entry):
    """
    Create a new project into the vwind table
    """
    sql = ''' INSERT INTO vwind(level,lat,lon, t, v)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, entry)
    conn.commit()
    return cur.lastrowid

# === *** ===

def rm(clist, str):
	for c in clist:
		str = str.replace(c, '')
	return str

def extract_variable(file, start_line, vartype = float):
	lines = []
	res = []
	lines.append(file[start_line].split("=")[1])
	k = start_line
	if ";" not in lines[-1]:
		while ";" not in lines[-1]:
			k+=1
			lines.append(file[k])

	lines[-1] = lines[-1].split(";")[0]


	for line in lines:
		for x in line.split(","):
			if len(x.strip()):
				try:
					res.append(vartype(x))
				except Exception as e:
					pass
			

	return res, k

def pressure_to_m_odg(p): #a rafiner de toute urgence
	return -8000*math.log(p/1013)

def parse_file():

	lines = []
	for x in open("vwind79.txt", "r"):
		lines.append(x[:-1])

	print("File loaded")

	#database creation and connection
	database = "/home/lhd/Desktop/wind.db"

	# create a database connection
	conn = create_connection(database)
	if not conn:
		print("database couldn't load")
		exit()


	#table creation
	create_table(conn, sql_create_vwind_table)

	data = False
	k = 0
	res = [[], [], [], [], []] #level, lat, lon, time, vwnd

	while k < len(lines):
		if not data:
			if "data:" in lines[k]:
				data = True
				print("Data from line ", k, " onwarads")
		else:
			if "level =" in lines[k]:
				print(lines[k])
				res[0], k = extract_variable(lines, k)
			if "lat =" in lines[k]:
				print(lines[k])
				res[1], k = extract_variable(lines, k)
			if "lon =" in lines[k]:
				print(lines[k])
				res[2], k = extract_variable(lines, k)
			if "time =" in lines[k]:
				print(lines[k])
				res[3], k = extract_variable(lines, k, int)
			if "vwnd =" in lines[k]:
				print(lines[k])
				res[4], k = extract_variable(lines, k)

		k +=1;
		

	print(" === filling the table ===")
	


	k = 0
	l = 0
	for level in res[0]:
		for lat in res[1]:
			for lon in res[2]:
				
				print(100*l/( len(res[0])*len(res[1])*len(res[2]) ))
				l += 1

				for time in res[3]:
					vwnd = res[4][k]
					value = (level, lat, lon, time, vwnd)
					create_entry(conn, value)
					k += 1
						

if __name__ == "__main__":
	parse_file()
