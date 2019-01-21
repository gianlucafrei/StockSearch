--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.3

-- Started on 2018-04-17 09:25:42 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 7 (class 2615 OID 16534)
-- Name: stocksearch; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA stocksearch;


ALTER SCHEMA stocksearch OWNER TO postgres;

--
-- TOC entry 1 (class 3079 OID 13241)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 3148 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 605 (class 1247 OID 16624)
-- Name: longest_strike_state; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.longest_strike_state AS (
	currentstrike integer,
	longeststrike integer,
	lastvalue numeric
);


ALTER TYPE public.longest_strike_state OWNER TO postgres;

--
-- TOC entry 213 (class 1255 OID 16605)
-- Name: calendar_end(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calendar_end() RETURNS integer
    LANGUAGE sql STABLE
    AS $$
select max(day) from stocksearch."Calendar"
$$;


ALTER FUNCTION public.calendar_end() OWNER TO postgres;

--
-- TOC entry 210 (class 1255 OID 16604)
-- Name: calendar_start(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calendar_start() RETURNS integer
    LANGUAGE sql STABLE
    AS $$
select min(day) from stocksearch."Calendar"
$$;


ALTER FUNCTION public.calendar_start() OWNER TO postgres;

--
-- TOC entry 203 (class 1255 OID 16626)
-- Name: longest_strike_finalizer(public.longest_strike_state); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.longest_strike_finalizer(s public.longest_strike_state) RETURNS integer
    LANGUAGE plpgsql
    AS $$
	BEGIN
		return s.longestStrike;
	END;
$$;


ALTER FUNCTION public.longest_strike_finalizer(s public.longest_strike_state) OWNER TO postgres;

--
-- TOC entry 211 (class 1255 OID 16625)
-- Name: longest_strike_reduce(public.longest_strike_state, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.longest_strike_reduce(s public.longest_strike_state, v numeric) RETURNS public.longest_strike_state
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.longest_strike_reduce(s public.longest_strike_state, v numeric) OWNER TO postgres;

--
-- TOC entry 208 (class 1255 OID 16574)
-- Name: calendar(date); Type: FUNCTION; Schema: stocksearch; Owner: postgres
--

CREATE FUNCTION stocksearch.calendar(_date date) RETURNS integer
    LANGUAGE sql STABLE
    AS $$
SELECT "day"
FROM stocksearch."Calendar"
WHERE "date" <= _date
ORDER BY "date" DESC
LIMIT 1;
$$;


ALTER FUNCTION stocksearch.calendar(_date date) OWNER TO postgres;

--
-- TOC entry 609 (class 1255 OID 16627)
-- Name: longest_strike(numeric); Type: AGGREGATE; Schema: public; Owner: postgres
--

CREATE AGGREGATE public.longest_strike(numeric) (
    SFUNC = public.longest_strike_reduce,
    STYPE = public.longest_strike_state,
    INITCOND = '(0,0,-1)',
    FINALFUNC = public.longest_strike_finalizer
);


ALTER AGGREGATE public.longest_strike(numeric) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 199 (class 1259 OID 16535)
-- Name: Calendar; Type: TABLE; Schema: stocksearch; Owner: postgres
--

CREATE TABLE stocksearch."Calendar" (
    day integer NOT NULL,
    date date NOT NULL
);


ALTER TABLE stocksearch."Calendar" OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 16540)
-- Name: Share; Type: TABLE; Schema: stocksearch; Owner: postgres
--

CREATE TABLE stocksearch."Share" (
    key character varying(50) NOT NULL,
    name character varying(50),
    isin character varying(50),
    "dataSource" character varying(50),
    currency character varying(10),
    description text,
    start integer,
    "end" integer
);


ALTER TABLE stocksearch."Share" OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 16558)
-- Name: ShareData; Type: TABLE; Schema: stocksearch; Owner: postgres
--

CREATE TABLE stocksearch."ShareData" (
    key character varying(50) NOT NULL,
    day integer NOT NULL,
    value numeric(12,2) NOT NULL,
    origin character varying(20) NOT NULL
);


ALTER TABLE stocksearch."ShareData" OWNER TO postgres;

--
-- TOC entry 3138 (class 0 OID 16535)
-- Dependencies: 199
-- Data for Name: Calendar; Type: TABLE DATA; Schema: stocksearch; Owner: postgres
--

INSERT INTO stocksearch."Calendar" VALUES (1, '2018-01-01');
INSERT INTO stocksearch."Calendar" VALUES (2, '2018-01-02');
INSERT INTO stocksearch."Calendar" VALUES (3, '2018-01-05');
INSERT INTO stocksearch."Calendar" VALUES (4, '2018-01-06');


--
-- TOC entry 3139 (class 0 OID 16540)
-- Dependencies: 200
-- Data for Name: Share; Type: TABLE DATA; Schema: stocksearch; Owner: postgres
--

INSERT INTO stocksearch."Share" VALUES ('apple', 'Apple', '100', 'test', 'TST', 'Steigt konstant', 1, 4);
INSERT INTO stocksearch."Share" VALUES ('logi', 'Logitech', '200', 'test', 'TST', 'Ist konkurs seit 3', 1, 2);
INSERT INTO stocksearch."Share" VALUES ('micro', 'Microsoft', '300', 'test', 'TST', 'Bleibt konstant', 1, 4);
INSERT INTO stocksearch."Share" VALUES ('usb', 'USB AG', '400', 'test', 'TST', 'Ist teuer', 2, 4);


--
-- TOC entry 3140 (class 0 OID 16558)
-- Dependencies: 201
-- Data for Name: ShareData; Type: TABLE DATA; Schema: stocksearch; Owner: postgres
--

INSERT INTO stocksearch."ShareData" VALUES ('apple', 1, 10.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('apple', 2, 11.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('apple', 3, 12.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('apple', 4, 13.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('logi', 1, 5.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('logi', 2, 4.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('logi', 3, 0.00, 'not-existend');
INSERT INTO stocksearch."ShareData" VALUES ('logi', 4, 0.00, 'not-existend');
INSERT INTO stocksearch."ShareData" VALUES ('micro', 1, 20.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('micro', 2, 20.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('micro', 3, 20.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('micro', 4, 20.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('usb', 1, 100.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('usb', 2, 110.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('usb', 3, 120.00, 'original');
INSERT INTO stocksearch."ShareData" VALUES ('usb', 4, 130.00, 'original');


--
-- TOC entry 3008 (class 2606 OID 16539)
-- Name: Calendar Calendar_pkey; Type: CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."Calendar"
    ADD CONSTRAINT "Calendar_pkey" PRIMARY KEY (day);


--
-- TOC entry 3012 (class 2606 OID 16562)
-- Name: ShareData ShareData_pkey; Type: CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."ShareData"
    ADD CONSTRAINT "ShareData_pkey" PRIMARY KEY (key, day);


--
-- TOC entry 3010 (class 2606 OID 16547)
-- Name: Share Share_pkey; Type: CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."Share"
    ADD CONSTRAINT "Share_pkey" PRIMARY KEY (key);


--
-- TOC entry 3015 (class 2606 OID 16563)
-- Name: ShareData day-calendar; Type: FK CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."ShareData"
    ADD CONSTRAINT "day-calendar" FOREIGN KEY (day) REFERENCES stocksearch."Calendar"(day);


--
-- TOC entry 3013 (class 2606 OID 16548)
-- Name: Share end-calendar; Type: FK CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."Share"
    ADD CONSTRAINT "end-calendar" FOREIGN KEY ("end") REFERENCES stocksearch."Calendar"(day);


--
-- TOC entry 3016 (class 2606 OID 16568)
-- Name: ShareData share-key; Type: FK CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."ShareData"
    ADD CONSTRAINT "share-key" FOREIGN KEY (key) REFERENCES stocksearch."Share"(key);


--
-- TOC entry 3014 (class 2606 OID 16553)
-- Name: Share start-calendar; Type: FK CONSTRAINT; Schema: stocksearch; Owner: postgres
--

ALTER TABLE ONLY stocksearch."Share"
    ADD CONSTRAINT "start-calendar" FOREIGN KEY (start) REFERENCES stocksearch."Calendar"(day);


-- Completed on 2018-04-17 09:25:43 CEST

--
-- PostgreSQL database dump complete
--

