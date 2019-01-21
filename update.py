import database
import requests
import simplejson as json
from tqdm import tqdm

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    This updater updates the stock data into the datebase.
"""

args = None
_connection = None

def _download_share_data(key, api_key):
    """
    Downloads the data of a share and returns the reponse
    """

    key = key.replace('\n', '')
    url = f'https://www.quandl.com/api/v3/datasets/{key}.json?column_index=1&api_key={api_key}'
    response = requests.get(url)
    data = json.loads(response.content)['dataset']
    return data

def _download_and_insert_in_tmp(key, api_key):
    data = _download_share_data(key, api_key)
    _insert_in_tmp_share_table(data)
    _insert_in_tmp_date_table(data)

def _read_share_keys():
    """
    Reades the file with the share ids and
    returs them as a list of strings.
    """

    print("Read indexed shares")
    with open(args.sharefile) as f:
        keys = f.readlines()

    # Filter out commented lines and look for #END tag
    # to skip the following shares
    keys = [k.replace('\n', '') for k in keys]

    if '#END' in keys:
        idx = keys.index('#END')
        keys = keys[:idx]
    
    keys = [k for k in keys if not k[0] == '#']

    return keys

def _extract_currency(description):
    """
    Extracts the currency out of the description of a share

    >>> _extract_currency('Share price and volume data for Anheuser-Busch InBev SA<br><br>Symbol: ABIT<br><br>ISIN: BE0974293251<br><br>Currency: CHF')
    'CHF'
    >>> _extract_currency('Currency CHF. For more information on this dataset, please see: <a href=http://www.six-swiss-exchange.com/shares/security_info_en.html?id=AT0000920863CHF4>http://www.six-swiss-exchange.com/shares/security_info_en.html?id=AT0000920863CHF4</a>')
    'unkown'
    """
    try:
        pattern = '<br>Currency: '
        start_idx = description.index(pattern)+len(pattern)
        return description[start_idx : start_idx+3] #The currency string has always langht 3
    except:
        return "unkown"

def _extract_isin(description):
    """
    Extracts the isin out of the description of a share
    >>> _extract_isin('Share price and volume data for Anheuser-Busch InBev SA<br><br>Symbol: ABIT<br><br>ISIN: BE0974293251<br><br>Currency: CHF')
    'BE0974293251'
    >>> _extract_isin('Currency CHF. For more information on this dataset, please see: <a href=http://www.six-swiss-exchange.com/shares/security_info_en.html?id=AT0000920863CHF4>http://www.six-swiss-exchange.com/shares/security_info_en.html?id=AT0000920863CHF4</a>')
    'unkown'
    """
    try:
        pattern = '<br>ISIN: '
        start_idx = description.index(pattern)+len(pattern)
        end_idx = description[start_idx:].index('<')+start_idx
        return description[start_idx : end_idx]
    except:
        return "unkown"

def _insert_in_tmp_share_table(data):
    """
    Inserts the data in the temporary share table.
    """
    description = data['description']
    values = (
        data['database_code'] + "/" + data['dataset_code'],
        data['name'],
        _extract_isin(description),
        "Quandl",
        _extract_currency(description),
        description,
        data['oldest_available_date'],
        data['newest_available_date'])

    sql = 'INSERT INTO "TmpShare" VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    _connection.execute(sql, values)

def _insert_in_tmp_date_table(data):
    """
    Insert the data in the temoprary share data table.
    """
    key = data['database_code'] + "/" + data['dataset_code']
    for entry in data['data']:
        date = entry[0]
        val  = entry[1]
        sql = 'INSERT INTO "TmpShareData" VALUES (%s, %s, %s)'
        _connection.execute(sql, (key, date, val))

def _fill_calendar_table():
    """
    Fills the calendar table
    """
    sql="""
    /*Create calendar*/
    INSERT INTO stocksearch."Calendar"

        SELECT 
            row_number() OVER (ORDER BY date) as day,
            date
        FROM
            "TmpShareData"
        GROUP BY
            date
        HAVING
            count(key) > 0
        ORDER BY
            date asc;
    """
    _connection.execute(sql)

def _fill_share_table():
    """
    Moves the data from the temporary share table to the real share table.s
    """
    
    sql="""
    insert into stocksearch."Share"
        select 
            tmp.key as key,
            tmp.name as name,
            tmp.isin as isin,
            tmp."dataSource" as dataSource,
            tmp.currency as currency,
            tmp.description as descriptio,
            s.day as start,
            e.day as end
        from
            "TmpShare" as tmp
        inner join
            stocksearch."Calendar" as s on tmp.start_date = s.date
        inner join
            stocksearch."Calendar" as e on tmp.end_date = e.date;
    """
    _connection.execute(sql)

def _move_temp_data_to_data(key):
    """
    Moves the data from the temporary share data table to
    the real share data table.
    Here we do also the gap filling.
    """
    sql="""
    SELECT
        %s as key,
        c.day as day,
        c.date as date,
        tmp.value as value
	FROM
        stocksearch."Calendar" as c
	LEFT OUTER JOIN
		(select * from "TmpShareData" where key=%s) as tmp
	    ON tmp.date = c.date
    ORDER BY
        c.day;
    """
    entries = _connection.execute(sql, (key, key))
    sql = """select * from stocksearch."Share" where key='{}';""".format(key)
    meta = _connection.execute(sql)
    meta = meta[0]

    # Here we make the gap filling according to out last value policy
    last_value = None
    for entry in entries:
        if entry['day'] < meta['start'] or entry['day'] > meta['end']:
            entry['value'] = 0
            entry['origin'] = "not-existend"
        elif entry['value'] is None:
            entry['value'] = last_value
            entry['origin'] = "gap-filled"
        else:
            entry['origin'] = "original"
        last_value = entry['value']
    
    #Now we need to save the entries
    for entry in entries:
        sql = 'INSERT INTO stocksearch."ShareData" VALUES (%s,%s,%s,%s)'
        values = (entry['key'], entry['day'], entry['value'], entry['origin'])
        _connection.execute(sql, values)

def _create_tmp_tables():
    """
    Creates the temporary tables to save the downloaded data
    """

    sql = """
    CREATE TEMPORARY TABLE "TmpShare"
    (
        key character varying(50) COLLATE pg_catalog."default" NOT NULL,
        name character varying(50) COLLATE pg_catalog."default",
        isin character varying(50) COLLATE pg_catalog."default",
        "dataSource" character varying(50) COLLATE pg_catalog."default",
        currency character varying(10) COLLATE pg_catalog."default",
        description text COLLATE pg_catalog."default",
        start_date date,
        end_date date
    );
    """
    _connection.execute(sql)
    sql = """
    CREATE TEMPORARY TABLE "TmpShareData"
    (
        key character varying(50) COLLATE pg_catalog."default" NOT NULL,
        date date NOT NULL,
        value numeric(12,2) NOT NULL
    );
    """
    _connection.execute(sql)

def _delete_all_data_in_db():
    print("Delete data")
    _connection.execute('DELETE FROM stocksearch."ShareData";')
    _connection.execute('DELETE FROM stocksearch."Share";')
    _connection.execute('DELETE FROM stocksearch."Calendar";')

def _init():

    api_key = read_api_key()   

    # Prepare database
    _create_tmp_tables()
    _delete_all_data_in_db()

    # Read keys
    keys = _read_share_keys()
    
    if args.limit > 0:
        keys = keys[:args.limit]

    print("Start downloading share data")
    for key in tqdm(keys):
        _download_and_insert_in_tmp(key, api_key)
    
    print("Fill calendar table")
    _fill_calendar_table()

    print("Fill share table")
    _fill_share_table()

    print("Move tmp data to data")
    for k in tqdm(keys):
        _move_temp_data_to_data(k)

def read_api_key():
    """
    Reads the api key from the api key file and returns it
    """
    with open(args.keyfile) as f:
        settings = json.loads(f.read())
    return settings["key"]

def db_init():

    print("Start database init script")
    print("Load database _connection")
    global _connection 
    _connection = database.PostgresqlConnection(args.connection)

    print("Start transaction")
    _connection.execute('START TRANSACTION;')

    try:
        _init()    
        print("End transaction")
        _connection.execute('End TRANSACTION;')
    except Exception as ex:
        print("[!] Init failed")
        print("[!]" + str(ex))
        _connection.execute('ROLLBACK;')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Stocksearch command line update')
    parser.add_argument('-c', '--connection', default="secured/postgres.json", help="<path> The path to the database connection file default secured/postgres.json")
    parser.add_argument('-k', '--keyfile', default="secured/quandlapikey.json", help="<path> Filepath for the api json default: secured/quandlapikey.json")
    parser.add_argument('-l', '--limit', default=0, type=int, help="Sets the maximum amount of downloaded shares\n 0 stands for infinity, Default 0")
    parser.add_argument('-s', '--sharefile', default="indexed_shares.txt", help="<path> Filepath to the list of indexed shares. Default indexed_shares.txt")

    args = parser.parse_args()
    db_init()