import mysql.connector
import os
import pandas as pd


def create_db(name):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )

    cursor = db.cursor()
    cursor.execute("CREATE DATABASE " + name)
    cursor.close()


def load_data(fname):
    return pd.read_csv('../data/' + fname)


def get_header_type(d):
    h_init = '('
    for i, col in d.items():
        h_init += i + ' '

        if col.dtype == int:
            h_init += 'INT(50)'
        else:
            h_init += 'VARCHAR(255)'

        if i == d.columns[-1]:
            h_init += ')'
        else:
            h_init += ', '

    return h_init


def get_d_format(n):
    f = '('
    for i in range(n):
        f += '%s'
        if i == n:
            f += ')'
        else:
            f += ', '
    return f


def create_table(fname, dbname):
    name = fname[:-4]
    data = load_data(fname)
    header = get_header_type(data)

    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=dbname
    )

    cursor = db.cursor()
    cursor.execute("CREATE TABLE " + name + header)

    format = get_d_format(len(data.columns))

    for i, row in data.iterrows():
        sql = 'INSERT INTO ' + name + ' VALUES ' + format
        cursor.execute(sql, tuple(row))
        db.commit()

    cursor.close()


def main():
    dbname = 'zillow_group_a'
    create_db(dbname)
    fnames = os.listdir('../data/')
    for n in fnames:
        create_table(n, dbname)


if __name__ == "__main__":
    host = 'localhost'
    user = 'root'
    password = 'root'
    main()