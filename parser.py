import engine as eg
from modgrammar import *
from datetime import date, datetime, timedelta

"""
    author: Gian-Luca Frei & Fedor Gamper
    date: 30.05.2018
    project: Stocksearch

    This parser translates the ssql (stocksearch query language :-) ) to sql for the postgres DB 
"""    

grammar_whitespace_mode = 'optional'

def format_date(date):
    return "{:04d}-{:02d}-{:02d}".format(date.year,date.month, date.day)

def today():
    date = datetime.today()
    date_str = format_date(date)
    return eg.Date(date_str)

def since(days_to_subtract):
    date = datetime.today() - timedelta(days=days_to_subtract)
    date_str = format_date(date)
    return eg.Date(date_str)

class Statement(Grammar):
    """
        >>> valid(Statement, "all shares")
        >>> valid(Statement, "all shares where value > 100")
        >>> valid(Statement, "all shares where value on 2013-06-21 >= 100")
        >>> valid(Statement, "get 'apple'")

        >>> stmt = parse(Statement, "all shares where (2>1)")
        >>> isinstance(stmt, eg.AllWhereStatement)
        True
    """
    grammar_collapse = True
    grammar = OR(REF("AllStatement"), REF("AllWhereStatement"), REF("Detail"))

class AllStatement(Grammar, eg.AllStatement):
    """
    >>> invalid(AllStatement, "all shares where 1<0")
    >>> valid(AllStatement, "all shares")
    """
    grammar = ("all shares")

    def grammar_elem_init(self, _):
        self.condition = eg.BooleanCondition(True)

class AllWhereStatement(Grammar, eg.AllWhereStatement):
    """
    >>> valid(AllWhereStatement, "all shares where (2>1)")
    >>> invalid(AllWhereStatement, "all shares (2>1)")
    """
    grammar = ("all shares where ", REF("Condition"))
    
    def grammar_elem_init(self, _):
        self.condition = self[1]

class Condition(Grammar):
    """
    >>> valid(Condition, "(2>1)")
    >>> valid(Condition, "2>1 or (2<2 and 1=1)")
    >>> valid(Condition, "value != 1")

    >>> cond = parse(Condition, "2>1 or (2<2 and 1=1)")
    >>> isinstance(cond, CombinedCondition)
    True

    >>> cond.comperator
    'or'
    """
    grammar_collapse = True
    grammar = OR(
        REF("CombinedCondition"),
        REF("FunctionCompareCondition"),
        REF("ParenthesedCondition"),
        REF('BooleanCondition'))

class ParenthesedCondition(Grammar, eg.ParenthesedCondition):
    """
    >>> valid(ParenthesedCondition, "(2>1)")
    >>> invalid(ParenthesedCondition, "(2>1")
    >>> invalid(ParenthesedCondition, "2>1")
    """
    grammar = ("(", REF("Condition"), ")")

    def grammar_elem_init(self, _):
        self.innerCondition = self[1]

class CombinedCondition(Grammar, eg.CombinedCondition):
    """
    >>> valid(CombinedCondition, "(2 > 1) AND value > 1")
    >>> valid(CombinedCondition, "value on 2001-01-01 > 100 or change from 2001-01-01 to 2002-01-01 <= change since 2 days")
    >>> valid(CombinedCondition, "2>1 or 2<2 and 1=1")
    """
    # HACK To waoid left recursion we allow on the right side no combined conditions
    left = OR(REF("FunctionCompareCondition"), REF("ParenthesedCondition"), REF('BooleanCondition'))
    grammar = (left, REF("BoolOperator"), REF("Condition"))

    def grammar_elem_init(self, _):
        self.leftCondition = self[0]
        self.comperator = self[1].string
        self.rightCondition = self[2]

class BooleanCondition(Grammar, eg.BooleanCondition):
    """
    >>> valid(BooleanCondition, "true")
    >>> valid(BooleanCondition, "false")
    >>> valid(Condition, "(true or false) or true and false or true")
    """
    grammar = OR('true', 'false')
    def grammar_elem_init(self, _):
        self.value = (self.string == "true")
             

class BoolOperator(Grammar):
    """
    >>> valid(BoolOperator, "AND")
    >>> invalid(BoolOperator, "NOT")
    """
    grammar = OR("and", "or")

class FunctionCompareCondition(Grammar, eg.FunctionCompareCondition):
    """
    >>> valid(FunctionCompareCondition, "value on 2001-01-01 > 100")
    >>> valid(FunctionCompareCondition, "change from 2001-01-01 to 2002-01-01 <= change since 2 days")
    
    >>> cond = parse(FunctionCompareCondition, "value on 2001-01-01 > 100")
    >>> isinstance(cond.leftFunction, Value)
    True

    >>> isinstance(cond.comparator, str)
    True
    """
    grammar = (REF("Function"), REF("Comperator"), REF("Function"))
    
    def grammar_elem_init(self, _):
        self.leftFunction = self[0]
        self.comparator = self[1].string
        self.rightFunction = self[2]

class Comperator(Grammar):
    """
    >>> valid(Comperator, "=")
    >>> invalid(Comperator, "==")
    """
    grammar = OR("!=", ">", ">=", "=", "<=", "<")

class Function(Grammar):
    """
    >>> valid(Function, "30.1")
    >>> valid(Function, "Change since 2001-01-01")
    >>> valid(Function, "value")
    >>> valid(Function, "average")
    >>> valid(Function, "variance")
    >>> valid(Function, "longest grow")

    >>> f = parse(Function, "20")
    >>> f.value
    20.0
    """
    grammar_collapse = True
    grammar = OR(REF("Decimal"), REF("Value"), REF("Change"), REF("Variance"), REF("Average"), REF("LongestGrow"))

class PosInteger(Grammar):
    """
    >>> valid(PosInteger, "21")
    >>> valid(PosInteger, "0")
    >>> invalid(PosInteger, "-31")
    >>> invalid(PosInteger, "31.31")
    """
    grammar = WORD('0-9')

class Decimal(Grammar, eg.Decimal):
    """
    >>> valid(Decimal, "-31.31")
    >>> valid(Decimal, "0")
    >>> invalid(Decimal, "31.12.31")
    >>> valid(Decimal, "20%")
    >>> valid(Decimal, "0%")
    >>> valid(Decimal, "0.10%")
    """

    grammar = (OPTIONAL('-'), WORD('0-9'), OPTIONAL('.', WORD('0-9')), OPTIONAL('%'))

    def grammar_elem_init(self, _):
        if(self.string[-1] == '%'):
            trimmed = self.string[:-1]
            self.value = float(trimmed) / 100
        else:
            self.value = float(self.string)
    

class Value(Grammar, eg.Value):
    """
    >>> valid(Value, "value on 2000-01-01")
    >>> valid(Value, "VALUE")
    >>> invalid(Value, "value since 2001-01-01")

    >>> value = parse(Value, "value on 2000-01-01")
    >>> str(value.date)
    '2000-01-01'

    >>> valuetoday = parse(Value, "value")
    >>> str(valuetoday.date)  == str(today())
    True
    """
    grammar = ("value", OPTIONAL("on", REF("Date")))

    def grammar_elem_init(self, _):
        if self[1] is None:
            self.date = today()
        else:
            self.date = eg.Date(self[1][1].string)

class Date(Grammar):
    """
    >>> valid(Date, "2013-01-01")
    >>> invalid(Date, "2003")
    """
    grammar = (WORD('0-9'), "-", WORD('0-9'), "-", WORD('0-9'))

class Change(Grammar, eg.Change):
    """
    >>> valid(Change, "change since 3 days")
    >>> valid(Change, "absolute change since 4 days")
    >>> invalid(Change, "change on 2000-01-12")

    >>> change = parse(Change, "change from 2000-01-01 to 2001-01-01")
    >>> str(change.timespan.start)
    '2000-01-01'
    """
    grammar = (OPTIONAL("absolute"), "change", REF("Timespan"))
    def grammar_elem_init(self, _):
        absolute = not (self[0] is None)
        timespan = self[2]
        self.absolute = absolute
        self.timespan = timespan

class Variance(Grammar, eg.Variance):
    """
    >>> valid(Variance, "variance")
    >>> valid(Variance, "variance from 2018-01-01 to 2018-01-02")
    >>> valid(Variance, "variance since 3 days")

    >>> invalid(Variance, "variance 2018-01-01")
    """
    grammar = ("variance", OPTIONAL(REF("Timespan")))
    def grammar_elem_init(self, _):
        
        if self[1] is None:
            self.timespan = eg.Always()
        else:
            self.timespan = self[1]

class Average(Grammar, eg.Average):
    """
    >>> valid(Average, "average")
    >>> valid(Average, "average from 2018-01-01 to 2018-01-02")
    >>> valid(Average, "average since 3 days")

    >>> invalid(Average, "average 2018-01-01")
    """
    grammar = ("average", OPTIONAL(REF("Timespan")))
    def grammar_elem_init(self, _):
        if self[1] is None:
            self.timespan = eg.Always()
        else:
            self.timespan = self[1]

class LongestGrow(Grammar, eg.LongestStrike):
    """
    >>> valid(LongestGrow, "longest grow")
    >>> valid(LongestGrow, "longest grow from 2018-01-01 to 2018-01-02")
    >>> valid(LongestGrow, "longest grow since 3 days")

    >>> invalid(LongestGrow, "longestgrow")
    >>> invalid(LongestGrow, "longest grow 2018-01-01")
    """
    grammar = ("longest grow", OPTIONAL(REF("Timespan")))
    def grammar_elem_init(self, _):
        if self[1] is None:
            self.timespan = eg.Always()
        else:
            self.timespan = self[1]

class Timespan(Grammar):
    """
    >>> fromTo = parse(Timespan, "FROM 2013-01-31 TO 2014-01-01")
    >>> str(fromTo.start), str(fromTo.end)
    ('2013-01-31', '2014-01-01')
    
    >>> since = parse(Timespan, "since 2000-01-01")
    >>> str(since.start)
    '2000-01-01'
    """
    grammar_collapse = True
    grammar = OR(REF("SinceDays"), REF("SinceDate"), REF("FromTo"))

class SinceDays(Grammar, eg.Timespan):
    """
    >>> valid(SinceDays, "since 4 days")
    """
    grammar = ("since", REF("PosInteger"), "days")

    def grammar_elem_init(self, _):
        since_days = int(self[1].string)
        self.start = since(since_days)
        self.end = today()

class SinceDate(Grammar, eg.Timespan):
    """
    >>> valid(SinceDate, "SINCE 2000-01-01")
    """
    grammar = ("since", REF("Date"))

    def grammar_elem_init(self, _):
        self.start = eg.Date(self[1].string)
        self.end = today()

class FromTo(Grammar, eg.Timespan):
    """
    >>> valid(FromTo, "FROM 2013-01-31 TO 2014-01-01")
    >>> invalid(FromTo, "From 3131-01 to 3101-01-01")
    """
    grammar = ("from", REF("Date"), "to", REF("Date"))

    def grammar_elem_init(self, _):
        self.start = eg.Date(self[1].string)
        self.end = eg.Date(self[3].string)

class Detail(Grammar, eg.DetailStatement):
    """
    >>> valid(Detail, "GET 'logi'")
    >>> invalid(Detail, "GET logi")
    """
    grammar = ("get", REF("String"))

    def grammar_elem_init(self, _):
        str = self[1]
        self.id = str.val

class AnythingButQuotation(Grammar):
    """
    >>> valid(AnythingButQuotation, "blablabla/njas")
    >>> invalid(AnythingButQuotation, "blabla'bla/njas")
    >>> invalid(AnythingButQuotation, "blabla`bla/njas")
    >>> invalid(AnythingButQuotation, '"blabla`bla/njas')
    """
    grammar = REPEAT(ANY_EXCEPT(['"', "'" "`"]))

class String(Grammar):
    """
    >>> valid(String, "'Blabla'")
    >>> valid(String, '"Foo"')
    >>> invalid(String, "'Foo")
    >>> parse(String, "'Foo'").val
    'Foo'
    """
    single = ("'", REF("AnythingButQuotation") ,"'")
    sqlStyle = ("`", REF("AnythingButQuotation") ,"`")
    double = ('"', REF("AnythingButQuotation") ,'"')
    grammar = OR(single, sqlStyle, double)

    def grammar_elem_init(self, _):
        self.val = self[0][1].string

def _lower_but_not_strings(ssql):
    """
        Makes the argument lower case but not what's between quotiation marks
        >>> _lower_but_not_strings("FooFooo 'Boo'>Foo")
        "foofooo 'Boo'>foo"
    """
    in_quotation = False
    quotation_marks = "'`" + '"'
    lowerString = ""
    for char in ssql:
        # Swap mode if quotation mark
        if char in quotation_marks: in_quotation = not in_quotation
        lowerString += (char if in_quotation else char.lower())
    return lowerString

def valid(clazz, string):
    string = string.lower()
    parser = clazz.parser()
    result = parser.parse_string(string)
    reminder = parser.remainder()
    if reminder != "":
        raise Exception(f"Not all imput is part of the result: \n String: {string}\n Reminder: {reminder}")

def invalid(clazz, string):
    try:
        valid(clazz, string)
    except:
        return
    raise(f"String: {string} was valid")

def parse(clazz, string):
    string = _lower_but_not_strings(string)
    parser = clazz.parser()
    result = parser.parse_string(string)
    return result

def parseStmt(input):
    return parse(Statement, input)

def get_all_grammar_classes():
    return [
    AllStatement,
    AllWhereStatement,
    Average,
    BoolOperator,
    BooleanCondition,
    Change,
    CombinedCondition,
    Comperator,
    Condition,
    Date,
    Decimal,
    Detail,
    FromTo,
    Function,
    FunctionCompareCondition,
    LongestGrow,
    ParenthesedCondition,
    PosInteger,
    SinceDate,
    SinceDays,
    Statement,
    String,
    Timespan,
    Value,
    Variance]

def print_grammar():
    
    for g in get_all_grammar_classes():
        for s in generate_ebnf(g, expand_terminals=True): print(s)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
