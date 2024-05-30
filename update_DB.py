import sqlite3
import Connect
from consts import *


def create_connection(db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_name: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Exception as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    c = None
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)
    return c, conn


def create_db():
    create_table_query = """CREATE TABLE IF NOT EXISTS computers (
        ip text NOT NULL,
        mac text NOT NULL,
        is_on INTEGER NOT NULL
    );
    """

    conn = create_connection(DB_NAME)
    c = None
    # create tables

    if conn is not None:
        # create projects table
        c, conn = create_table(conn, create_table_query)

    else:
        print("Error! cannot create the database connection.")
    return c, conn


def get_dict_data():
    cursor, connection = create_db()
    cursor.execute(GET_DATA_SQL_QUERY)
    comps_dict = {i[0]: i[2] for i in cursor}
    return comps_dict


def main():
    state = 0  # 1 - Computer on. 0 - Computer off

    cursor, connection = create_db()
    successful_cons = Connect.get_successful_cons()

    """ For loop inserting new computers into the database """
    for i in successful_cons.keys():
        cursor.execute("""SELECT ip,mac FROM computers WHERE ip=? """, (i,))
        result = cursor.fetchone()
        if not result:
            cursor.execute(INSERT_SQL_QUERY, (i, successful_cons[i], 1))
    connection.commit()

    cursor.execute("SELECT * FROM computers")
    table = cursor.fetchall()

    """ For loop changing the computer's states """
    for index, row in enumerate(table):
        if row[0] in successful_cons:
            state = 1
        else:
            state = 0
        cursor.execute(UPDATE_ROW_QUERY, (state, index + 1))
    connection.commit()


if __name__ == '__main__':
    main()
