--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

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
-- Name: baked_recomends; Type: TABLE; Schema: public; Owner: s8weber; Tablespace: 
--

CREATE TABLE baked_recomends (
    isbn_lookup character varying(16) NOT NULL,
    isbn character varying(16) NOT NULL,
    poppop integer NOT NULL
);


ALTER TABLE public.baked_recomends OWNER TO s8weber;

--
-- Name: institution; Type: TABLE; Schema: public; Owner: splurge; Tablespace: 
--

CREATE TABLE institution (
    institution_id bigint NOT NULL,
    institution character varying(16) NOT NULL
);


ALTER TABLE public.institution OWNER TO splurge;

--
-- Name: institution_institution_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge
--

CREATE SEQUENCE institution_institution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.institution_institution_id_seq OWNER TO splurge;

--
-- Name: institution_institution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge
--

ALTER SEQUENCE institution_institution_id_seq OWNED BY institution.institution_id;


--
-- Name: item; Type: TABLE; Schema: public; Owner: splurge; Tablespace: 
--

CREATE TABLE item (
    item_id bigint NOT NULL,
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    isbn character varying(16) NOT NULL
);


ALTER TABLE public.item OWNER TO splurge;

--
-- Name: item_item_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge
--

CREATE SEQUENCE item_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_item_id_seq OWNER TO splurge;

--
-- Name: item_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge
--

ALTER SEQUENCE item_item_id_seq OWNED BY item.item_id;


--
-- Name: related_isbn_item_cache; Type: TABLE; Schema: public; Owner: s8weber; Tablespace: 
--

CREATE TABLE related_isbn_item_cache (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    isbn character varying(16)
);


ALTER TABLE public.related_isbn_item_cache OWNER TO s8weber;

--
-- Name: relateditemcache; Type: TABLE; Schema: public; Owner: splurge; Tablespace: 
--

CREATE TABLE relateditemcache (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    linked_item_no character varying(16) NOT NULL,
    linked_institution integer NOT NULL
);


ALTER TABLE public.relateditemcache OWNER TO splurge;

--
-- Name: relateditemcache2; Type: TABLE; Schema: public; Owner: s8weber; Tablespace: 
--

CREATE TABLE relateditemcache2 (
    item_no character varying(16) NOT NULL,
    institution bigint NOT NULL,
    linked_item_no character varying(16) NOT NULL,
    linked_institution integer NOT NULL,
    isbn character varying(16)
);


ALTER TABLE public.relateditemcache2 OWNER TO s8weber;

--
-- Name: relateditemcache_linked_institution_seq; Type: SEQUENCE; Schema: public; Owner: splurge
--

CREATE SEQUENCE relateditemcache_linked_institution_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.relateditemcache_linked_institution_seq OWNER TO splurge;

--
-- Name: relateditemcache_linked_institution_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge
--

ALTER SEQUENCE relateditemcache_linked_institution_seq OWNED BY relateditemcache.linked_institution;


--
-- Name: transaction; Type: TABLE; Schema: public; Owner: splurge; Tablespace: 
--

CREATE TABLE transaction (
    transaction_id bigint NOT NULL,
    transact_time timestamp(6) with time zone NOT NULL,
    item_no character varying(16) NOT NULL,
    patron_id character varying(32) NOT NULL,
    institution bigint NOT NULL
);


ALTER TABLE public.transaction OWNER TO splurge;

--
-- Name: transaction_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: splurge
--

CREATE SEQUENCE transaction_transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transaction_transaction_id_seq OWNER TO splurge;

--
-- Name: transaction_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splurge
--

ALTER SEQUENCE transaction_transaction_id_seq OWNED BY transaction.transaction_id;


--
-- Name: institution_id; Type: DEFAULT; Schema: public; Owner: splurge
--

ALTER TABLE ONLY institution ALTER COLUMN institution_id SET DEFAULT nextval('institution_institution_id_seq'::regclass);


--
-- Name: item_id; Type: DEFAULT; Schema: public; Owner: splurge
--

ALTER TABLE ONLY item ALTER COLUMN item_id SET DEFAULT nextval('item_item_id_seq'::regclass);


--
-- Name: transaction_id; Type: DEFAULT; Schema: public; Owner: splurge
--

ALTER TABLE ONLY transaction ALTER COLUMN transaction_id SET DEFAULT nextval('transaction_transaction_id_seq'::regclass);


--
-- Name: institution_institution_key; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY institution
    ADD CONSTRAINT institution_institution_key UNIQUE (institution);


--
-- Name: institution_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY institution
    ADD CONSTRAINT institution_pkey PRIMARY KEY (institution_id);


--
-- Name: item_item_no_institution_isbn_key; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY item
    ADD CONSTRAINT item_item_no_institution_isbn_key UNIQUE (item_no, institution, isbn);


--
-- Name: item_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY item
    ADD CONSTRAINT item_pkey PRIMARY KEY (item_id);


--
-- Name: transaction_id_pkey; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_id_pkey PRIMARY KEY (transaction_id);


--
-- Name: transaction_transact_time_item_no_patron_id_institutio_key; Type: CONSTRAINT; Schema: public; Owner: splurge; Tablespace: 
--

ALTER TABLE ONLY transaction
    ADD CONSTRAINT transaction_transact_time_item_no_patron_id_institutio_key UNIQUE (transact_time, item_no, patron_id, institution);


--
-- Name: backed_recomend_isbn_lookup; Type: INDEX; Schema: public; Owner: s8weber; Tablespace: 
--

CREATE INDEX backed_recomend_isbn_lookup ON baked_recomends USING btree (isbn_lookup);


--
-- Name: item_isbn; Type: INDEX; Schema: public; Owner: splurge; Tablespace: 
--

CREATE INDEX item_isbn ON item USING btree (isbn);

ALTER TABLE item CLUSTER ON item_isbn;


--
-- Name: itemno_institution; Type: INDEX; Schema: public; Owner: splurge; Tablespace: 
--

CREATE INDEX itemno_institution ON item USING btree (item_no, institution);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO splurge;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--
