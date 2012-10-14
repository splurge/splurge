--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

DROP INDEX public.itemno_institution;
DROP INDEX public.item_isbn;
DROP INDEX public.backed_recomend_isbn_lookup;
ALTER TABLE ONLY public.transaction DROP CONSTRAINT transaction_transact_time_item_no_patron_id_institutio_key;
ALTER TABLE ONLY public.transaction DROP CONSTRAINT transaction_id_pkey;
ALTER TABLE ONLY public.item DROP CONSTRAINT item_pkey;
ALTER TABLE ONLY public.item DROP CONSTRAINT item_item_no_institution_isbn_key;
ALTER TABLE ONLY public.institution DROP CONSTRAINT institution_pkey;
ALTER TABLE ONLY public.institution DROP CONSTRAINT institution_institution_key;
ALTER TABLE public.transaction ALTER COLUMN transaction_id DROP DEFAULT;
ALTER TABLE public.item ALTER COLUMN item_id DROP DEFAULT;
ALTER TABLE public.institution ALTER COLUMN institution_id DROP DEFAULT;
DROP SEQUENCE public.transaction_transaction_id_seq;
DROP TABLE public.transaction;
DROP SEQUENCE public.relateditemcache_linked_institution_seq;
DROP TABLE public.relateditemcache2;
DROP TABLE public.relateditemcache;
DROP TABLE public.related_isbn_item_cache;
DROP SEQUENCE public.item_item_id_seq;
DROP TABLE public.item;
DROP SEQUENCE public.institution_institution_id_seq;
DROP TABLE public.institution;
DROP TABLE public.baked_recomends;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: baked_recomends; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE baked_recomends (
    isbn_lookup character varying(16) NOT NULL,
    isbn character varying(16) NOT NULL,
    poppop integer NOT NULL
);


ALTER TABLE public.baked_recomends OWNER TO splurge_user;

--
-- Name: institution; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE institution (
    institution_id bigint NOT NULL,
    institution character varying(16) NOT NULL,
    version timestamp
);


ALTER TABLE public.institution OWNER TO splurge_user;

--
-- Name: institution_institution_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge_user
--

CREATE SEQUENCE institution_institution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.institution_institution_id_seq OWNER TO splurge_user;

--
-- Name: institution_institution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge_user
--

ALTER SEQUENCE institution_institution_id_seq OWNED BY institution.institution_id;


--
-- Name: institution_institution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: splurge_user
--

SELECT pg_catalog.setval('institution_institution_id_seq', 1, false);


--
-- Name: item; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE item (
    item_id bigint NOT NULL,
    institution bigint,
    item_no character varying(16) NOT NULL,
    isbn character varying(16) NOT NULL
);


ALTER TABLE public.item OWNER TO splurge_user;

--
-- Name: item_item_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge_user
--

CREATE SEQUENCE item_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_item_id_seq OWNER TO splurge_user;

--
-- Name: item_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge_user
--

ALTER SEQUENCE item_item_id_seq OWNED BY item.item_id;


--
-- Name: item_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: splurge_user
--

SELECT pg_catalog.setval('item_item_id_seq', 1, false);


--
-- Name: related_isbn_item_cache; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE related_isbn_item_cache (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    isbn character varying(16)
);


ALTER TABLE public.related_isbn_item_cache OWNER TO splurge_user;

--
-- Name: relateditemcache; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE relateditemcache (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    linked_item_no character varying(16) NOT NULL,
    linked_institution integer NOT NULL
);


ALTER TABLE public.relateditemcache OWNER TO splurge_user;

--
-- Name: relateditemcache2; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE relateditemcache2 (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    linked_item_no character varying(16) NOT NULL,
    linked_institution integer NOT NULL,
    isbn character varying(16)
);


ALTER TABLE public.relateditemcache2 OWNER TO splurge_user;

--
-- Name: relateditemcache_linked_institution_seq; Type: SEQUENCE; Schema: public; Owner: splurge_user
--

CREATE SEQUENCE relateditemcache_linked_institution_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.relateditemcache_linked_institution_seq OWNER TO splurge_user;

--
-- Name: relateditemcache_linked_institution_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge_user
--

ALTER SEQUENCE relateditemcache_linked_institution_seq OWNED BY relateditemcache.linked_institution;


--
-- Name: relateditemcache_linked_institution_seq; Type: SEQUENCE SET; Schema: public; Owner: splurge_user
--

SELECT pg_catalog.setval('relateditemcache_linked_institution_seq', 1, false);


--
-- Name: transaction; Type: TABLE; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE TABLE transaction (
    transaction_id bigint NOT NULL,
    institution bigint,
    transact_time timestamp with time zone NOT NULL,
    item_no character varying(16) NOT NULL,
    patron_id character varying(32) NOT NULL
);


ALTER TABLE public.transaction OWNER TO splurge_user;

--
-- Name: transaction_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge_user
--

CREATE SEQUENCE transaction_transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transaction_transaction_id_seq OWNER TO splurge_user;

--
-- Name: transaction_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge_user
--

ALTER SEQUENCE transaction_transaction_id_seq OWNED BY transaction.transaction_id;


--
-- Name: transaction_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: splurge_user
--

SELECT pg_catalog.setval('transaction_transaction_id_seq', 1, false);


--
-- Name: institution_id; Type: DEFAULT; Schema: public; Owner: splurge_user
--

ALTER TABLE ONLY institution ALTER COLUMN institution_id SET DEFAULT nextval('institution_institution_id_seq'::regclass);


--
-- Name: item_id; Type: DEFAULT; Schema: public; Owner: splurge_user
--

ALTER TABLE ONLY item ALTER COLUMN item_id SET DEFAULT nextval('item_item_id_seq'::regclass);


--
-- Name: transaction_id; Type: DEFAULT; Schema: public; Owner: splurge_user
--

ALTER TABLE ONLY transaction ALTER COLUMN transaction_id SET DEFAULT nextval('transaction_transaction_id_seq'::regclass);


--
-- Data for Name: baked_recomends; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY baked_recomends (isbn_lookup, isbn, poppop) FROM stdin;
\.


--
-- Data for Name: institution; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY institution (institution_id, institution) FROM stdin;
\.


--
-- Data for Name: item; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY item (item_id, item_no, institution, isbn) FROM stdin;
\.


--
-- Data for Name: related_isbn_item_cache; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY related_isbn_item_cache (item_no, institution, isbn) FROM stdin;
\.


--
-- Data for Name: relateditemcache; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY relateditemcache (item_no, institution, linked_item_no, linked_institution) FROM stdin;
\.


--
-- Data for Name: relateditemcache2; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY relateditemcache2 (item_no, institution, linked_item_no, linked_institution, isbn) FROM stdin;
\.


--
-- Data for Name: transaction; Type: TABLE DATA; Schema: public; Owner: splurge_user
--

COPY transaction (transaction_id, transact_time, item_no, patron_id, institution) FROM stdin;
\.


--
-- Name: institution_institution_key; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY institution
    ADD CONSTRAINT institution_institution_key UNIQUE (institution);


--
-- Name: institution_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY institution
    ADD CONSTRAINT institution_pkey PRIMARY KEY (institution_id);


--
-- Name: item_item_no_institution_isbn_key; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY item
    ADD CONSTRAINT item_item_no_institution_isbn_key UNIQUE (item_no, institution, isbn);


--
-- Name: item_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY item
    ADD CONSTRAINT item_pkey PRIMARY KEY (item_id);


--
-- Name: transaction_id_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_id_pkey PRIMARY KEY (transaction_id);


--
-- Name: transaction_transact_time_item_no_patron_id_institutio_key; Type: CONSTRAINT; Schema: public; Owner: splurge_user; Tablespace: 
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_transact_time_item_no_patron_id_institutio_key UNIQUE (transact_time, item_no, patron_id, institution);


--
-- Name: backed_recomend_isbn_lookup; Type: INDEX; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE INDEX backed_recomend_isbn_lookup ON baked_recomends USING btree (isbn_lookup);


--
-- Name: item_isbn; Type: INDEX; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE INDEX item_isbn ON item USING btree (isbn);

ALTER TABLE item CLUSTER ON item_isbn;


--
-- Name: itemno_institution; Type: INDEX; Schema: public; Owner: splurge_user; Tablespace: 
--

CREATE INDEX itemno_institution ON item USING btree (item_no, institution);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;

-- recommend_items():
-- Find others that took out the same item
-- Find out what other items they took out during a given time range
-- Count how many times those other items were taken out
-- Cap the popularity to avoid the Harry Potter effect
CREATE OR REPLACE FUNCTION recommend_items(
    target_isbn TEXT,
    max_rank INT DEFAULT 20,
    start_year TEXT DEFAULT NULL,
    end_year TEXT DEFAULT NULL
)
RETURNS TABLE (original_isbn TEXT, suggested_isbn TEXT, pop BIGINT) AS $$
  WITH recommendations AS (
    SELECT isbn_look, i.isbn, tf.patron_id, tf.item_no, tf.institution, COUNT(*) AS popularity
    FROM transaction tf
      INNER JOIN (
        SELECT isbn AS isbn_look, patron_id, t.institution
        FROM transaction t
          INNER JOIN item i ON t.item_no = i.item_no
        WHERE isbn = $1
        GROUP BY isbn_look, patron_id, t.institution
      ) AS usr
        ON tf.patron_id = usr.patron_id
          AND tf.institution = usr.institution
      INNER JOIN item i
        ON tf.item_no = i.item_no
          AND tf.institution = i.institution
      WHERE i.isbn <> $1
        AND tf.transact_time BETWEEN to_timestamp(COALESCE($3, '1900'),'YYYY')
         AND to_timestamp(COALESCE($4, '2999'),'YYYY')
    GROUP BY isbn_look, i.isbn, tf.patron_id, tf.item_no, tf.institution
    HAVING COUNT(*) > 1
    ORDER BY popularity DESC, isbn_look, tf.item_no
  )
  SELECT isbn_look::TEXT, isbn::TEXT, popularity::BIGINT FROM (
    SELECT isbn_look, isbn, popularity, RANK() OVER (PARTITION BY isbn_look ORDER BY popularity DESC, isbn) AS rank
    FROM recommendations
  ) AS final
  WHERE final.rank < $2; 
$$ LANGUAGE SQL STABLE ROWS 10;

-- Avoid sequential scans on the transaction table if we're lucky
-- enough to have a reasonably restricted date range
CREATE INDEX transaction_time ON transaction (transact_time);

--
-- PostgreSQL database dump complete
--

