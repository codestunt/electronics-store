--
-- PostgreSQL database dump
--

\restrict BkEa3VmXeuZVG46wb70zbv8sB2iindWEUtdAmttcUCPcQK2HpaxDrCJRG4Y7C5l

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: newsletter_status; Type: TYPE; Schema: public; Owner: electro_user
--

CREATE TYPE public.newsletter_status AS ENUM (
    'pending',
    'subscribed',
    'unsubscribed'
);


ALTER TYPE public.newsletter_status OWNER TO electro_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: electro_user
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.categories OWNER TO electro_user;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO electro_user;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: newsletter_subscribers; Type: TABLE; Schema: public; Owner: electro_user
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


ALTER TABLE public.newsletter_subscribers OWNER TO electro_user;

--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.newsletter_subscribers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.newsletter_subscribers_id_seq OWNER TO electro_user;

--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.newsletter_subscribers_id_seq OWNED BY public.newsletter_subscribers.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: electro_user
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer,
    product_id integer,
    quantity integer,
    price numeric(10,2)
);


ALTER TABLE public.order_items OWNER TO electro_user;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO electro_user;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: electro_user
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id integer,
    total numeric(10,2),
    status character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.orders OWNER TO electro_user;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO electro_user;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: electro_user
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(255),
    description text,
    price numeric(10,2),
    image_path character varying(255),
    rating numeric(2,1),
    review_count integer,
    stock_quantity integer DEFAULT 10,
    bestseller boolean DEFAULT false,
    bestseller_label character varying(50),
    review_summary text,
    tag character varying(100),
    category_id integer
);


ALTER TABLE public.products OWNER TO electro_user;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO electro_user;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: electro_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying(100),
    email character varying(100),
    password character varying(255)
);


ALTER TABLE public.users OWNER TO electro_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: electro_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO electro_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: electro_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: newsletter_subscribers id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.newsletter_subscribers ALTER COLUMN id SET DEFAULT nextval('public.newsletter_subscribers_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.categories (id, name) FROM stdin;
1	audio
2	cameras
3	microwaves
4	phones
5	projectors
7	tvs
8	fridges
\.


--
-- Data for Name: newsletter_subscribers; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.newsletter_subscribers (id, email, status, confirm_token, confirmed_at, unsubscribed_at, created_at, updated_at) FROM stdin;
1	mbama@gmail.com	subscribed	\N	\N	\N	2026-02-03 03:14:51.20456	2026-02-03 03:14:51.20456
2	nandy@gmail.com	subscribed	\N	\N	\N	2026-02-03 06:03:00.000272	2026-02-03 06:03:00.000272
3	joana@gmail.com	subscribed	\N	\N	\N	2026-02-25 03:03:46.176703	2026-02-25 03:03:46.176703
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.order_items (id, order_id, product_id, quantity, price) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.orders (id, user_id, total, status, created_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.products (id, name, description, price, image_path, rating, review_count, stock_quantity, bestseller, bestseller_label, review_summary, tag, category_id) FROM stdin;
43	Audio-Technica AT-LP60X Turntable	Fully automatic belt-drive turntable with built-in phono preamp.	149.00	images/products/audio_at_lp60x.jpg	4.6	3120	18	f	\N	Great starter deck for spinning your vinyl collection.	audio	1
42	Yamaha RX-V6A 7.2-ch AV Receiver	7.2-channel AVR with Dolby Atmos, DTS:X and 8K pass-through.	699.00	images/products/audio_yamaha_rx_v6a.jpg	4.5	940	8	f	\N	Feature-rich hub for your home theater speakers.	audio	1
41	Sennheiser Momentum 4 Wireless	Elegant wireless ANC headphones with a relaxed, detailed sound.	349.00	images/products/audio_sennheiser_momentum4.jpg	4.7	2310	22	f	\N	Audiophile-leaning tuning and marathon battery life.	audio	1
40	JBL Charge 5 Bluetooth Speaker	Rugged portable speaker with powerful bass and long battery life.	179.00	images/products/audio_jbl_charge_5.jpg	4.6	9210	40	f	\N	Waterproof party speaker you can take anywhere.	audio	1
39	Sonos Arc Soundbar	Dolby Atmos soundbar for cinematic TV audio and seamless multiroom.	899.00	images/products/audio_sonos_arc.jpg	4.7	2750	15	f	\N	Big, room-filling sound with easy TV setup.	audio	1
38	Apple AirPods Pro (2nd Gen)	True wireless earbuds with Adaptive Transparency and ANC.	249.00	images/products/audio_airpods_pro_2.jpg	4.6	8420	50	f	\N	Pocketable ANC earbuds with great iPhone integration.	audio	1
37	Bose QuietComfort Ultra Headphones	Premium ANC with spatial audio and a plush, lightweight fit.	429.00	images/products/audio_bose_qc_ultra.jpg	4.7	3870	26	f	\N	Immersive listening with top-tier comfort.	audio	1
36	Sony WH-1000XM5 Headphones	Flagship over-ear ANC headphones with superb sound and comfort.	449.00	images/products/audio_sony_wh1000xm5.jpg	4.8	5120	30	f	\N	Class-leading noise cancelling for travel and work.	audio	1
29	Headphones	\N	99.95	images/products/headphones.jpg	\N	\N	0	f	\N	0	audio	1
18	Speakers	HiFi Speakers Pair(Lava Red)	2390.00	images/products/speakers.jpg	4.6	96000	5	t	pick	0	audio	1
14	GoPro HERO10	Action camera	499.00	images/products/gopro.jpg	5.0	1600	15	t	pick	None	None	2
11	Canon DSLR Camera 	18MP with 2 lenses	880.06	images/products/canon.jpg	4.5	3499	0	f	bundle	0		2
75	Hisense 28L Grill Microwave Oven	Compact microwave with 5 power levels and grill function.	329.00	images/products/microwave_hisense_28l.jpg	4.6	1850	24	f	\N	Affordable and reliable option for small households	microwave, hisense, grill	3
74	Toshiba 25L Compact Digital Microwave	Digital controls with child lock and quick-start options.	299.00	images/products/microwave_toshiba_25l.jpg	4.6	2100	28	f	\N	Simple, compact, and powerful everyday microwave	microwave, toshiba, compact	3
73	Whirlpool 30L Convection Microwave Oven	11 auto cook menus with grill and convection features.	369.00	images/products/microwave_whirlpool_30l.jpg	4.5	1700	30	f	\N	Energy-efficient and perfect for quick meals	microwave, whirlpool, convection	3
72	Samsung 32L Smart Grill Microwave	Grill and microwave combo with ceramic enamel interior.	399.00	images/products/microwave_samsung_32l.jpg	4.7	2460	22	f	\N	Compact and stylish with durable ceramic coating	microwave, samsung, grill	3
71	Sharp 34L Convection Microwave Oven	Microwave and convection combo with multiple auto menus.	449.00	images/products/microwave_sharp_34l.jpg	4.6	1980	18	f	\N	Reliable all-rounder with great performance for families	microwave, sharp, convection	3
70	Breville Quick Touch Crisp Microwave	Sensor IQ technology with a crisper pan for golden, crispy meals.	599.00	images/products/microwave_breville_quicktouch.jpg	4.9	2280	12	f	\N	Perfect for crisp reheating and even cooking every time	microwave, breville, crisp	3
69	LG NeoChef 42L Smart Inverter Microwave	Smart inverter for precise heating and defrosting with touch controls.	499.00	images/products/microwave_lg_neochef_42l.jpg	4.7	3120	20	f	\N	Modern microwave with advanced cooking control and easy clean interior	microwave, lg, smart inverter	3
68	Panasonic 44L Inverter Microwave Oven	Large capacity microwave with inverter technology for even heating.	549.00	images/products/microwave_panasonic_44l.jpg	4.8	2750	25	f	\N	Spacious and efficient with consistent cooking results	microwave, panasonic, inverter	3
51	Motorola Edge 40 Pro	Clean Android and excellent charging speeds.	1099.00	images/products/phone_motorola_edge40_pro.jpg	4.5	860	26	f	\N	Surprisingly polished experience	phone, smartphone, android, motorola	4
50	Sony Xperia 1 V	Creator-focused 4K HDR OLED and manual camera tools.	1799.00	images/products/phone_sony_xperia_1v.jpg	4.4	740	12	f	\N	Loved by videographers	phone, smartphone, android, sony	4
49	OPPO Find X7	Premium design, bright display, strong cameras.	1199.00	images/products/phone_oppo_find_x7.jpg	4.5	980	18	f	\N	Well balanced flagship	phone, smartphone, android, oppo	4
48	Xiaomi 14 Pro	Leica camera tuning and flagship specs.	1299.00	images/products/phone_xiaomi_14_pro.jpg	4.6	1650	22	f	\N	Sharp screen, speedy charging	phone, smartphone, android, xiaomi	4
47	OnePlus 12	Snapdragon 8 Gen, fast charging, smooth display.	1199.00	images/products/phone_oneplus_12.jpg	4.6	2105	35	f	\N	Great performance per dollar	phone, smartphone, android, oneplus	4
46	Google Pixel 8 Pro	Tensor G3 with excellent AI camera and clean Android.	1399.00	images/products/phone_pixel_8_pro.jpg	4.7	3180	28	f	\N	Top-tier still photography	phone, smartphone, android, pixel	4
45	Samsung Galaxy S24 Ultra	200MP camera, long battery life, S-Pen.	1899.00	images/products/phone_galaxy_s24_ultra.jpg	4.8	4210	30	f	\N	Feature-packed flagship	phone, smartphone, android, samsung	4
44	Apple iPhone 15 Pro	A17 Pro, ProMotion display, pro-grade camera system.	1499.00	images/products/phone_iphone15pro.jpg	4.9	5120	25	f	\N	Blazing fast and great camera	phone, smartphone, iOS	4
12	Samsung Galaxy S22	128GB, 5G Smartphone,	799.00	images/products/galaxy.jpg	5.0	5488	12	t	pick	\N	phone	4
59	Optoma UHD55 4K Smart Home Projector	True 4K UHD with HDR10 and gaming mode at 240Hz.	1899.00	images/products/projector_optoma_uhd55.jpg	4.7	1900	22	f	\N	Balanced choice for both movies and gaming	projector, optoma, 4k	5
58	Anker Nebula Cosmos Max	Compact 4K HDR projector with built-in Dolby Digital Plus speakers.	1299.00	images/products/projector_anker_cosmos.jpg	4.6	2500	15	f	\N	Excellent all-in-one portable entertainment projector	projector, anker, 4k, portable	5
57	XGIMI Horizon Pro 4K Projector	Compact and portable smart 4K projector with Android TV.	1599.00	images/products/projector_xgimi_horizon_pro.jpg	4.8	3120	20	f	\N	Sleek design, top-notch brightness, great sound	projector, xgimi, smart	5
56	ViewSonic PX701HD 1080p Projector	Bright 3500-lumen 1080p projector ideal for home entertainment.	799.00	images/products/projector_viewsonic_px701hd.jpg	4.6	2800	25	f	\N	Great value projector for movies and gaming	projector, viewsonic, 1080p	5
55	LG HU715QW CineBeam 4K Laser Projector	Ultra short throw laser projector with built-in streaming apps.	3199.00	images/products/projector_lg_hu715qw.jpg	4.7	1600	10	f	\N	Impressive ultra short throw projection with sharp details	projector, lg, 4k, laser	5
54	Sony VPL-VW590ES 4K HDR Projector	Native 4K SXRD projector with ultra-realistic color and detail.	5499.00	images/products/projector_sony_vw590es.jpg	4.9	1380	8	f	\N	Outstanding cinematic performance with deep blacks	projector, sony, 4k	5
53	BenQ TK850i Smart Home Projector	Android TV built-in with 4K HDR projection and vivid color accuracy.	1899.00	images/products/projector_benq_tk850i.jpg	4.7	1750	18	f	\N	Smart projector with excellent brightness for daylight use	projector, benq, 4k	5
52	Epson EH-TW9400 4K PRO-UHD Projector	Ultra HD 4K PRO-UHD with high dynamic contrast and HDR10 support.	2799.00	images/products/projector_epson_tw9400.jpg	4.8	2250	12	f	\N	Cinema-grade visuals with stunning color performance	projector, epson, 4k	5
35	Philips OLED 907	OLED display with Ambilight and Bowers & Wilkins sound system built in.	1399.00	images/products/philips_oled907_tv.jpg	4.8	3200	9	f	PREMIUM DESIGN	Beautiful picture and immersive audio experience.	OLED, Ambilight, Smart TV	7
34	Vizio Quantum Pro	Affordable QLED brilliance with superior HDR and Dolby Vision.	699.00	images/products/vizio_quantum_tv.jpg	4.6	2100	18	f	TOP PICK	Great color reproduction and high brightness for its price.	QLED, HDR, Smart TV	7
33	Hisense Laser TV 100\\"	Massive 100-inch projection display powered by laser technology.	2499.00	images/products/hisense_laser100_tv.jpg	4.8	3500	6	f	CINEMA EXPERIENCE	Big-screen entertainment with laser precision.	tv,Laser TV, 100-inch, HDR	7
32	TCL-Mini-LED Q7 TV	Ultra-slim QLED panel with Mini-LED backlighting for deep contrast.	849.00	images/products/tcl_q7_tv.jpg	4.7	2780	14	f	SUMMER VALUE	Beautiful colors and responsive motion for gaming and streaming.	tv,Mini-LED, QLED, 4K	7
31	Samsung Neo QLED 8K TV	Next-generation 8K resolution with Quantum Matrix Technology for lifelike clarity.	1999.00	images/products/samsung_neo8k_tv.jpg	4.9	4120	10	f	PREMIUM FLAGSHIP	Unmatched detail and ultra-bright picture quality.	tv	7
15	LG UHD TV	60 inch Smart 4K TV	649.00	images/products/lg.jpg	4.4	2982	9	t	bundle	\N	tv	7
67	Electrolux 609L UltimateTaste French Door Fridge	Designed for even cooling and food preservation with TasteSeal technology.	3399.00	images/products/fridge_electrolux_609l.jpg	4.9	2210	14	f	\N	Elegant and energy-efficient with advanced food freshness system	fridge, electrolux, french door	8
66	Hisense 514L Black Steel Fridge	Stylish design with multi-airflow and frost-free freezer.	1899.00	images/products/fridge_hisense_514l.jpg	4.6	1750	25	f	\N	Great value and sleek black finish for modern kitchens	fridge, hisense	8
65	Fisher & Paykel 605L ActiveSmart Fridge	Adaptive cooling technology and humidity-controlled compartments.	3099.00	images/products/fridge_fisher_605l.jpg	4.8	2010	10	f	\N	Premium performance with intelligent cooling control	fridge, fisher, activesmart	8
64	Haier 482L Quad Door Fridge	Compact quad-door fridge with independent freezer zones.	2199.00	images/products/fridge_haier_482l.jpg	4.5	1520	18	f	\N	Modern design with flexible storage options	fridge, haier, quad door	8
63	Westinghouse 520L French Door Fridge	Spacious family-size design with adjustable glass shelves.	2599.00	images/products/fridge_westinghouse_520l.jpg	4.6	1800	20	f	\N	Reliable and affordable with energy-efficient operation	fridge, westinghouse	8
62	Bosch 600L Series 8 Bottom Mount Fridge	German engineering with VitaFresh Plus and multi-airflow system.	2999.00	images/products/fridge_bosch_series8.jpg	4.7	2600	15	f	\N	Top-tier cooling performance with durable build	fridge, bosch, bottom mount	8
61	LG 570L French Door InstaView Fridge	Knock twice to see inside — energy-efficient with inverter compressor.	3299.00	images/products/fridge_lg_instaview.jpg	4.8	3850	12	f	\N	Spacious and elegant design with great cooling efficiency	fridge, lg, french door	8
60	Samsung Family Hub 680L French Door Fridge	Smart fridge with Wi-Fi connectivity, touch screen, and internal cameras.	3699.00	images/products/fridge_samsung_familyhub.jpg	4.9	4120	8	f	\N	High-tech fridge perfect for smart homes	fridge, samsung, smart	8
30	Tv Camera	\N	899.99	images/products/tvCamera.jpg	\N	\N	10	f	\N	4	tv	\N
13	Apple iPad Pro	12.9 inch Liquid Retina Display	1099.00	images/products/ipadpro.jpg	4.5	7320	10	t	bundle	0	phone	\N
17	Projector	Yaber K2S Native 1080P 4K	699.00	images/products/projector.jpg	4.4	518	7	t	bundle	0	projector	\N
20	Fridge	LG DF-V700BSCL 642L French Door	4599.00	images/products/fridge.jpg	4.7	2754	6	t	pick	0	fridge	\N
19	Washing Machine	10Kg EasyCare Front Load	999.00	images/products/washing_machine.jpg	4.9	4927	4	t	bundle	\N		\N
16	Microwave	Sharp R395EST 1200W 34L Inventer	349.00	images/products/microwave.jpg	4.3	3100	6	t	pick	0	microwave	\N
1	Canon R6	Full-frame mirrorless camera	2499.00	images/products/camera_canon_r6.jpg	4.8	1200	10	f	\N	Professional mirrorless performance	camera, canon	2
2	DJI Osmo 3	4K handheld gimbal camera	499.00	images/products/camera_dji_osmo3.jpg	4.6	870	15	f	\N	Smooth cinematic footage	camera, dji	2
3	Fujifilm XT5	40MP APS-C mirrorless	2199.00	images/products/camera_fuji_xt5.jpg	4.9	950	8	f	\N	Excellent color science and detail	camera, fujifilm	2
4	Sony A7 IV	33MP full-frame mirrorless	2699.00	images/products/camera_sony_a7iv.jpg	4.9	1500	6	t	PRO PICK	Outstanding hybrid shooter	camera, sony	2
5	Panasonic GH6	Micro Four Thirds video beast	1999.00	images/products/camera_panasonic_gh6.jpg	4.7	620	9	f	\N	Excellent video capabilities	camera, panasonic	2
6	Nikon Z6 II	Full-frame hybrid mirrorless	2399.00	images/products/camera_nikon_z6ii.jpg	4.8	800	7	f	\N	Balanced performance for pros	camera, nikon	2
7	GoPro Hero 12	Action camera 5.3K	599.00	images/products/camera_gopro_hero12.jpg	4.6	2000	20	f	\N	Rugged action performer	camera, gopro	2
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: electro_user
--

COPY public.users (id, full_name, email, password) FROM stdin;
1	Hwengwe	hwengwe@gmail.com	scrypt:32768:8:1$HawcCzl2TJsW5n4K$e32b490dc4fc68f7b6ddad378ccaf2b8f6347863dee8f79a2d740bfcdf6d4695fc6eae6717b307f76b1569e1e58409ae60abe5a43e1b1b60c7a6520f6fad4899
2	Ngoni	ngoni@gmail.com	scrypt:32768:8:1$57FddC9EJSizBDzr$06bf63a04877d6bab8dba614f6a31e242ed56289f4193226876daa2e6af42d453ca8373f5dda6229355b3881be37b8eb5be0da09c9463bbd8cd5fac5f408c562
3	Ndunde	ndunde@gmail.com	scrypt:32768:8:1$TbbrBzbqYke8sdxG$50277660ae62ff49f3f9141c79be72a2ac0a264da248eeb12eccf9c236b3645a6dab25439d2f0fc1e9c75a79c905216eb9b3f35693b15b9d88826d9957c014d4
4	Brainy	joe1mtaika@gmail.com	scrypt:32768:8:1$DjXpNhfMJ5pa4OEf$414b441badab1dab99073484ddbe0b7e99b9e61ccbf4387e597bdbae5aff48b6a7b83ad85e511b3f2d7f54bb5718c354b04a5a1ac628e24d332653db38a75572
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.categories_id_seq', 8, true);


--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.newsletter_subscribers_id_seq', 3, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.order_items_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.products_id_seq', 8, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: electro_user
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: newsletter_subscribers newsletter_subscribers_email_key; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.newsletter_subscribers
    ADD CONSTRAINT newsletter_subscribers_email_key UNIQUE (email);


--
-- Name: newsletter_subscribers newsletter_subscribers_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.newsletter_subscribers
    ADD CONSTRAINT newsletter_subscribers_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: products fk_products_category; Type: FK CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE RESTRICT;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: electro_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict BkEa3VmXeuZVG46wb70zbv8sB2iindWEUtdAmttcUCPcQK2HpaxDrCJRG4Y7C5l

