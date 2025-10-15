--
-- PostgreSQL database dump
--

\restrict P56LJea8nrJRAKPK47T4DEB1Pb5MFqgpkquSLD8AEngYXLr2KbbEyO2IZj4iMfC

-- Dumped from database version 17.6 (Debian 17.6-0+deb13u1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: pw_manager_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO pw_manager_user;

--
-- Name: secrettype; Type: TYPE; Schema: public; Owner: pw_manager_user
--

CREATE TYPE public.secrettype AS ENUM (
    'CREDENTIAL',
    'NOTE',
    'DOCUMENT',
    'creditcard'
);


ALTER TYPE public.secrettype OWNER TO pw_manager_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pw_manager_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pw_manager_user;

--
-- Name: secret; Type: TABLE; Schema: public; Owner: pw_manager_user
--

CREATE TABLE public.secret (
    id integer NOT NULL,
    type character varying(10) NOT NULL,
    vault_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    data_encrypted bytea NOT NULL,
    encrypted_secret_key character varying NOT NULL,
    secret_key_iv character varying NOT NULL,
    secret_iv character varying NOT NULL
);


ALTER TABLE public.secret OWNER TO pw_manager_user;

--
-- Name: secret_id_seq; Type: SEQUENCE; Schema: public; Owner: pw_manager_user
--

CREATE SEQUENCE public.secret_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.secret_id_seq OWNER TO pw_manager_user;

--
-- Name: secret_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pw_manager_user
--

ALTER SEQUENCE public.secret_id_seq OWNED BY public.secret.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: pw_manager_user
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    email character varying NOT NULL,
    password character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_key character varying NOT NULL,
    salt character varying NOT NULL,
    iv character varying NOT NULL,
    last_login timestamp with time zone DEFAULT now(),
    mfa_enabled boolean NOT NULL,
    otp_secret character varying
);


ALTER TABLE public."user" OWNER TO pw_manager_user;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: pw_manager_user
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO pw_manager_user;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pw_manager_user
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: vault; Type: TABLE; Schema: public; Owner: pw_manager_user
--

CREATE TABLE public.vault (
    id integer NOT NULL,
    name character varying NOT NULL,
    owner_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vault OWNER TO pw_manager_user;

--
-- Name: vault_id_seq; Type: SEQUENCE; Schema: public; Owner: pw_manager_user
--

CREATE SEQUENCE public.vault_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vault_id_seq OWNER TO pw_manager_user;

--
-- Name: vault_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pw_manager_user
--

ALTER SEQUENCE public.vault_id_seq OWNED BY public.vault.id;


--
-- Name: secret id; Type: DEFAULT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.secret ALTER COLUMN id SET DEFAULT nextval('public.secret_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: vault id; Type: DEFAULT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.vault ALTER COLUMN id SET DEFAULT nextval('public.vault_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: pw_manager_user
--

COPY public.alembic_version (version_num) FROM stdin;
de7fbd2ad16d
\.


--
-- Data for Name: secret; Type: TABLE DATA; Schema: public; Owner: pw_manager_user
--

COPY public.secret (id, type, vault_id, created_at, updated_at, data_encrypted, encrypted_secret_key, secret_key_iv, secret_iv) FROM stdin;
8	credential	4	2025-10-14 11:52:47.839575+00	2025-10-14 11:52:47.839581+00	\\x585a75693434694f37385131366f575655736a413838436b5744423545493773594c795246533751617247552b4e6b4b624e4e484c764271716935436e52764d4573786b6b47734e734a4966585955716b36736a71566b67654364766f4c385065695479685742336142456a4c772f6b746d4c3870364e5579487854446b6e6e6e466b562f7a746f646b3337624c45312f586c494c63696a4255304d6c4a614c5563795630493951746d39767975673d	US20a2iFvj4JmTpNTlNSqggfMoIMPncpucew814sVdz1KYQgXok+bbR78X95+BbK	g5goHIHdgCCHuAko	AaIBIROimjCIIcCU
9	note	4	2025-10-14 11:59:43.305176+00	2025-10-14 11:59:43.30518+00	\\x3253702f764e78652f7546536c48646c716738374c3554456d69456647446544692b4445306465757638653450794f33317a584f414979687278534c51667a5650564244356571376b4d6235766964456450424532515946615a4a5a70395973544f364c3872447a51702f362f72593d	DTEPgLvh1rMBYfVkeYoV636CXCxbSGwA9csXPJ7ceW2N5fp1SFpEjB0loyxpYv2k	X7XB0sJYBapkXo5b	cBNJlSFvLdVMuLwA
10	creditcard	4	2025-10-14 12:00:34.108166+00	2025-10-14 12:00:34.10817+00	\\x51415062766147564d6e7435316c6a7732746c7a57547152697339487a70474848634b535747754b4c37444b7362304a304c30596479676a4743395264514b433971712b7443706950504b5352562b563733546b4e4a573047456e4153427252596a546d6c644933575174534978387279686636754e643056507435533169416e535a6b426735704b545a686b48676e6d776a7a6c61652b37773072487379743656722f533261727a5441793735337263386869664b636463364262374e784d4d6c6c6f4c6a742f3264524f68314e732b455543746e5a34394b6764564258785a306c53462b655353413d3d	lOwag9qvy6guHIJ1tx3+Aq6tYUt84NVcfezVJlT0g/BTa261zaq7LLiEgh6AVvZZ	noUd1ptxVP6gQFjO	SCITY047UJJEhl/R
11	note	5	2025-10-15 13:12:58.678341+00	2025-10-15 13:12:58.678346+00	\\x74377653327a3538673477306e427048475264715066346955396f5158706d583767487a687a316e397232657a346c647243437348786a75746175332f4349626f6a7232	g1Ocntj5SQgIxB5JSOK/LvGDLjo14EKUtDNwGB1COpyJm5BaSfFPDQTJc2Erk0Db	UyU5nta2f9VTwjr0	Ijg7yQZVXX4/WEzK
12	creditcard	5	2025-10-15 13:13:12.503773+00	2025-10-15 13:13:12.503779+00	\\x6763424b3556356c2b6d7462533075546b514152674b4a394f4b6261426e516b50636a2b466564764f547a48516b4b6d7779684e2f796c6d31686945636a634635386a4e4a443961463856466f495a6d5a764e61415a476170356a714a2b37395a4b3850674755554f65512b4c2f65626b6f6e2b4e324c4a79624c6175565763342b4761486a344969566c7745595a2f7954785245396754566f63515265634a574e784c6855327072616c52343470533855764d584434684372645a563759376a6b55306138534e35332f5833513d3d	y2ckB1h7/Oj8B8NGC4Vr96UL6znZ8VkF6jIP2DAiTgVZTeuf2LQ3G2YkxD3kTkrA	CMvtbL9+zc8/l6yl	4l/LWezEMskTPsI6
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: pw_manager_user
--

COPY public."user" (id, email, password, created_at, user_key, salt, iv, last_login, mfa_enabled, otp_secret) FROM stdin;
9	ritschlorenz1565656@gmail.com	$2b$12$KnEpkAYke80FVEE.07OHpe3l0v3MteQG8VNjNAzEGG6Eo4j0fsVrO	2025-10-15 12:27:14.410445+00	string	string	string	2025-10-15 12:27:14.410453+00	f	\N
10	ritschlorenz143333@gmail.com	$2b$12$kd2WdagkkXNr0Lldc15L/ex0JHlWTwlJ0eB5UEy0RTr/r7FNYycRm	2025-10-15 12:31:48.142318+00	string	string	string	2025-10-15 12:31:48.142325+00	f	\N
8	ritschlorenz14@gmail.com	$2b$12$8T7tKvbRbY8HQQZz4dP6iuNBvyXD9N9OivbVD6XHkO3/65nHCD/Qa	2025-10-12 15:39:09.56332+00	Fe1SFTHofGDUDLT60jhbyiTE3wbGH+eI7f1vZGnh5b6eVsskhHIyHo2mxGnsWJPc	ku0XMJ2qcCV9xMprxRcaRQ==	q4a/1I6Ql+Klcmy/	2025-10-15 12:59:10.700448+00	t	DMPLZ5PJLQLHBB72SM3WO2N26QGGU3TZ
11	ritschlorenz1434x@gmail.com	$2b$12$bC7wy02xCpeqflkpN.cV2ux.jADdwLHJf0xF9Amlr8j3/jYsyCDRu	2025-10-15 13:07:30.705568+00	AMig1Tbb1K7v+sf666ROExwIxiWHrGIsM8N/AP0i995TvL2iTqLVPYK60itUc7jg	PMobIeXlGJNlcNkIXwUgYQ==	H0BB2wI3950te1gA	2025-10-15 13:08:19.115383+00	t	SEDZOHXESJA3M67EKGU73BHBYHKDAYU4
\.


--
-- Data for Name: vault; Type: TABLE DATA; Schema: public; Owner: pw_manager_user
--

COPY public.vault (id, name, owner_id, created_at, updated_at) FROM stdin;
4	Private	8	2025-10-12 15:39:21.805854+00	2025-10-12 15:39:21.805858+00
5	Private	11	2025-10-15 13:12:42.235979+00	2025-10-15 13:12:42.235984+00
\.


--
-- Name: secret_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pw_manager_user
--

SELECT pg_catalog.setval('public.secret_id_seq', 12, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pw_manager_user
--

SELECT pg_catalog.setval('public.user_id_seq', 11, true);


--
-- Name: vault_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pw_manager_user
--

SELECT pg_catalog.setval('public.vault_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: secret secret_pkey; Type: CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.secret
    ADD CONSTRAINT secret_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: vault vault_pkey; Type: CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.vault
    ADD CONSTRAINT vault_pkey PRIMARY KEY (id);


--
-- Name: ix_secret_id; Type: INDEX; Schema: public; Owner: pw_manager_user
--

CREATE INDEX ix_secret_id ON public.secret USING btree (id);


--
-- Name: ix_secret_vault_id; Type: INDEX; Schema: public; Owner: pw_manager_user
--

CREATE INDEX ix_secret_vault_id ON public.secret USING btree (vault_id);


--
-- Name: ix_user_id; Type: INDEX; Schema: public; Owner: pw_manager_user
--

CREATE INDEX ix_user_id ON public."user" USING btree (id);


--
-- Name: ix_vault_id; Type: INDEX; Schema: public; Owner: pw_manager_user
--

CREATE INDEX ix_vault_id ON public.vault USING btree (id);


--
-- Name: secret secret_vault_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.secret
    ADD CONSTRAINT secret_vault_id_fkey FOREIGN KEY (vault_id) REFERENCES public.vault(id);


--
-- Name: vault vault_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pw_manager_user
--

ALTER TABLE ONLY public.vault
    ADD CONSTRAINT vault_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--

\unrestrict P56LJea8nrJRAKPK47T4DEB1Pb5MFqgpkquSLD8AEngYXLr2KbbEyO2IZj4iMfC

