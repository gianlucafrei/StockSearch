/* First day in the calendar */
CREATE OR REPLACE FUNCTION calendar_start()
    RETURNS integer
    LANGUAGE 'sql'
    STABLE
AS $BODY$
select min(day) from stocksearch."Calendar"
$BODY$;

ALTER FUNCTION calendar_start()
    OWNER TO postgres;

/* Last day in the calendar */
CREATE OR REPLACE FUNCTION calendar_end()
    RETURNS integer
    LANGUAGE 'sql'
    STABLE
AS $BODY$
select max(day) from stocksearch."Calendar"
$BODY$;

ALTER FUNCTION calendar_end()
    OWNER TO postgres;
	
SELECT calendar_start(), calendar_end();