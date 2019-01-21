/* Wee need a type for the state of the reduce function */
DROP TYPE IF EXISTS longest_strike_state CASCADE;

CREATE TYPE longest_strike_state as (
    currentStrike       integer,
    longestStrike       integer,
    lastValue           decimal
);

/* This function updates the state for each value in the reduce*/
CREATE OR REPLACE FUNCTION longest_strike_reduce(s longest_strike_state, v decimal) RETURNS longest_strike_state AS $$
	BEGIN
		IF s.lastValue != -1 AND v > s.lastValue THEN
			s.currentStrike = s.currentStrike + 1;
		ELSE
			/* The strike is finished */
			s.currentStrike = 0;
		END IF;
		
		IF s.currentStrike > s.longestStrike THEN
				s.longestStrike = s.currentStrike;
		END IF;
		s.lastValue = v;
		return s;
	END;
$$ LANGUAGE plpgsql;


/* This function pickes the final value out of the state of the reduce function*/
CREATE OR REPLACE FUNCTION longest_strike_finalizer(s longest_strike_state) RETURNS integer AS $$
	BEGIN
		return s.longestStrike;
	END;
$$ LANGUAGE plpgsql;

SELECT longest_strike_finalizer(longest_strike_reduce('(6,4, 4)', 5));

/* And this composes everything to one function*/
CREATE AGGREGATE longest_strike(decimal)
(
	sfunc = longest_strike_reduce,
	finalfunc = longest_strike_finalizer,
	stype = longest_strike_state,
    initcond = '(0,0,-1)'
);

/* Just to test if it works */
select key, longest_strike(value)
	from stocksearch."ShareData"
	group by key;