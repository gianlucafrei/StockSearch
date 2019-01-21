from itertools import groupby

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch
"""

def normalize_sql(sql):
    """
        Removes tabs and spaces from a sql string to test sql statements for equality
        >>> normalize_sql("bla bla   bla")
        'bla bla bla'
    """
    s = sql.replace('\n', ' ').replace('\t', ' ')
    # Reduce multible space to one
    res = ''.join(' ' if is_space else ''.join(chars) for is_space, chars in groupby(s, str.isspace))

    if res[-1] == ' ': res = res[:-1]

    return res

class DbField():
    """
    This class is used to represent a field in the database.
    This is useful to abstract the real database field names
    >>> print(DbField("name"))
    "name"
    """
    def __init__(self, _tbname):
        self._tbname = _tbname
    def __str__(self):
        return f'"{self._tbname}"'
    def __repr__(self):
        return self.__str__()

class Table(DbField):
    """
    Represents a name in the database
    >>> table = Table("Share", name="name", key="id")
    >>> str(table)
    'Share'
    
    >>> table = Table("Share", name="name", key="id")
    >>> print(table.name)
    "name"

    """
    def __init__(self, _tbname, **columns):
        super().__init__(_tbname)
        for key, value in columns.items():
            setattr(self, key, DbField(value))

    def __str__(self):
        return self._tbname