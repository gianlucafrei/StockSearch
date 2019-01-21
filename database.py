import pg8000
import json

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    This script handels the connection with the Postgres database.
"""

def read_settings(connection_file):
    with open(connection_file) as f:
        settings = json.loads(f.read())
    return settings

def list_to_dic(list, descriptions):
    dic = {}
    for idx, val in enumerate(list):
        key = descriptions[idx]
        dic[key] = val
    return dic

class PostgresqlConnection(object):

    verbose = False

    def __init__(self, connection_file):
        settings = read_settings(connection_file)
        self.connection = pg8000.connect(
                                user=settings['db-user'],
                                password=settings['db-password'],
                                database=settings['db-database'])

    def execute(self, sql, arg=None):
        try:

            if self.verbose:
                print(f'SQL: {sql} : {arg}')

            with self.connection.cursor() as cursor:
                # print("SQL: " + sql)
                if arg is None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, arg)
                try:
                    if cursor.rowcount > 0:
                        
                        # Here we transform the list into a dictionary
                        result = cursor.fetchall()
                        if cursor.description is not None:

                            desc = list(map(lambda l: l[0].decode('utf-8'), cursor.description))
                            dic  = [list_to_dic(r, desc) for r in result]
                            return dic

                        else:
                            return []
                    else:
                        return []
                except pg8000.ProgrammingError as ex:
                    if ex.args[0] != "no result set":
                        raise ex

        except:
            print("Error while executing sql statement: {}".format(sql))
            raise

    def close(self):
        self.connection.close()

def get_connecction(connection_file):
    return PostgresqlConnection(connection_file)
