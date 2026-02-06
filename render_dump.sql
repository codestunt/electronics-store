--
-- PostgreSQL database dump
--

\restrict vgOpOoPUitSk7I4NjSzpunFfIuicaYBw5ZTSIQNLElAA9VifrWr9Ar4fMQMcuwA

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg12+2)
-- Dumped by pg_dump version 18.1 (Ubuntu 18.1-1.pgdg24.04+2)

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: newsletter_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.newsletter_status AS ENUM (
    'pending',
    'subscribed',
    'unsubscribed'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: newsletter_subscribers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.newsletter_subscribers (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    status public.newsletter_status DEFAULT 'pending'::public.newsletter_status,
    confirm_token uuid,
    confirmed_at timestamp without time zone,
    unsubscribed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.newsletter_subscribers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.newsletter_subscribers_id_seq OWNED BY public.newsletter_subscribers.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer,
    product_id integer,
    quantity integer,
    price numeric(10,2)
);


--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id integer,
    total numeric(10,2),
    status character varying(50),
    created_at timestamp without time zone
);


--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(255),
    description text,
    price numeric(10,2),
    image_path character varying(255),
    rating numeric(2,1),
    review_count integer,
    category character varying(50),
    stock_quantity integer DEFAULT 10,
    bestseller boolean DEFAULT false,
    bestseller_label character varying(50),
    review_summary text,
    tag character varying(100)
);


--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying(100),
    email character varying(100),
    password character varying(255)
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: newsletter_subscribers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.newsletter_subscribers ALTER COLUMN id SET DEFAULT nextval('public.newsletter_subscribers_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (id, name) FROM stdin;
\.


--
-- Data for Name: newsletter_subscribers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.newsletter_subscribers (id, email, status, confirm_token, confirmed_at, unsubscribed_at, created_at, updated_at) FROM stdin;
1	mbama@gmail.com	subscribed	\N	\N	\N	2026-02-03 03:14:51.20456	2026-02-03 03:14:51.20456
2	nandy@gmail.com	subscribed	\N	\N	\N	2026-02-03 06:03:00.000272	2026-02-03 06:03:00.000272
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.order_items (id, order_id, product_id, quantity, price) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (id, user_id, total, status, created_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, description, price, image_path, rating, review_count, category, stock_quantity, bestseller, bestseller_label, review_summary, tag) FROM stdin;
1	VoltMax 4K	Ultra HD Smart TV	1299.99	/static/images/products/voltmax.jpg	4.7	128	TVs	10	t	Top Pick	\N	\N
11	Canon DSLR Camera 	18MP with 2 lenses	880.06	images/products/canon.jpg	4.5	3499	Cameras	0	f	bundle	0	
12	Samsung Galaxy S22	128GB, 5G Smartphone,	799.00	images/products/galaxy.jpg	5.0	5488	Phones	12	t	pick	\N	phone
13	Apple iPad Pro	12.9 inch Liquid Retina Display	1099.00	images/products/ipadpro.jpg	4.5	7320	Tablets	10	t	bundle	0	phone
14	GoPro HERO10	Action camera	499.00	images/products/gopro.jpg	5.0	1600	Cameras	15	t	pick	None	None
15	LG UHD TV	60 inch Smart 4K TV	649.00	images/products/lg.jpg	4.4	2982	TVs	9	t	bundle	\N	tv
16	Microwave	Sharp R395EST 1200W 34L Inventer	349.00	images/products/microwave.jpg	4.3	3100	Appliance	6	t	pick	0	microwave
17	Projector	Yaber K2S Native 1080P 4K	699.00	images/products/projector.jpg	4.4	518	Visual	7	t	bundle	0	projector
18	Speakers	HiFi Speakers Pair(Lava Red)	2390.00	images/products/speakers.jpg	4.6	96000	Audio	5	t	pick	0	audio
19	Washing Machine	10Kg EasyCare Front Load	999.00	images/products/washing_machine.jpg	4.9	4927	Appliances	4	t	bundle	\N	
20	Fridge	LG DF-V700BSCL 642L French Door	4599.00	images/products/fridge.jpg	4.7	2754	Appliances	6	t	pick	0	fridge
29	Headphones	\N	99.95	images/products/headphones.jpg	\N	\N	audio	0	f	\N	0	audio
30	Tv Camera	\N	899.99	images/products/tvCamera.jpg	\N	\N	\N	10	f	\N	4	tv
31	Samsung Neo QLED 8K TV	Next-generation 8K resolution with Quantum Matrix Technology for lifelike clarity.	1999.00	images/products/samsung_neo8k_tv.jpg	4.9	4120	TVs	10	f	PREMIUM FLAGSHIP	Unmatched detail and ultra-bright picture quality.	tv
32	TCL-Mini-LED Q7 TV	Ultra-slim QLED panel with Mini-LED backlighting for deep contrast.	849.00	images/products/tcl_q7_tv.jpg	4.7	2780	TVs	14	f	SUMMER VALUE	Beautiful colors and responsive motion for gaming and streaming.	tv,Mini-LED, QLED, 4K
33	Hisense Laser TV 100"	Massive 100-inch projection display powered by laser technology.	2499.00	images/products/hisense_laser100_tv.jpg	4.8	3500	TVs	6	f	CINEMA EXPERIENCE	Big-screen entertainment with laser precision.	tv,Laser TV, 100-inch, HDR
34	Vizio Quantum Pro	Affordable QLED brilliance with superior HDR and Dolby Vision.	699.00	images/products/vizio_quantum_tv.jpg	4.6	2100	TVs	18	f	TOP PICK	Great color reproduction and high brightness for its price.	QLED, HDR, Smart TV
35	Philips OLED 907	OLED display with Ambilight and Bowers & Wilkins sound system built in.	1399.00	images/products/philips_oled907_tv.jpg	4.8	3200	TVs	9	f	PREMIUM DESIGN	Beautiful picture and immersive audio experience.	OLED, Ambilight, Smart TV
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, full_name, email, password) FROM stdin;
1	Hwengwe	hwengwe@gmail.com	scrypt:32768:8:1$HawcCzl2TJsW5n4K$e32b490dc4fc68f7b6ddad378ccaf2b8f6347863dee8f79a2d740bfcdf6d4695fc6eae6717b307f76b1569e1e58409ae60abe5a43e1b1b60c7a6520f6fad4899
2	Ngoni	ngoni@gmail.com	scrypt:32768:8:1$57FddC9EJSizBDzr$06bf63a04877d6bab8dba614f6a31e242ed56289f4193226876daa2e6af42d453ca8373f5dda6229355b3881be37b8eb5be0da09c9463bbd8cd5fac5f408c562
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, false);


--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.newsletter_subscribers_id_seq', 2, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: newsletter_subscribers newsletter_subscribers_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.newsletter_subscribers
    ADD CONSTRAINT newsletter_subscribers_email_key UNIQUE (email);


--
-- Name: newsletter_subscribers newsletter_subscribers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.newsletter_subscribers
    ADD CONSTRAINT newsletter_subscribers_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict vgOpOoPUitSk7I4NjSzpunFfIuicaYBw5ZTSIQNLElAA9VifrWr9Ar4fMQMcuwA

