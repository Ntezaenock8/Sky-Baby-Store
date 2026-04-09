--
-- PostgreSQL database dump
--

\restrict JCMgQWW91NIVobJIxq6uefTGcSALzZvlZsY3SkIGaf59oB4FExK246IbX3SeujN

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cart; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cart (
    id integer NOT NULL,
    user_id integer,
    product_id integer,
    quantity integer DEFAULT 1
);


--
-- Name: cart_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cart_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cart_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cart_id_seq OWNED BY public.cart.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer,
    product_id integer,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL
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
    total numeric(10,2) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: product_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_images (
    id integer NOT NULL,
    product_id integer NOT NULL,
    image_url text NOT NULL,
    image_order integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: product_images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: product_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_images_id_seq OWNED BY public.product_images.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    stock integer DEFAULT 0,
    image_url text,
    category character varying(100),
    action character varying(50),
    discount numeric(5,2) DEFAULT 0
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
    name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password text NOT NULL,
    role character varying(10) DEFAULT 'customer'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: cart id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart ALTER COLUMN id SET DEFAULT nextval('public.cart_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: product_images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images ALTER COLUMN id SET DEFAULT nextval('public.product_images_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: cart; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cart (id, user_id, product_id, quantity) FROM stdin;
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.order_items (id, order_id, product_id, quantity, price) FROM stdin;
1	1	1	1	15000.00
3	2	1	2	15000.00
5	3	1	1	15000.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (id, user_id, total, status, created_at) FROM stdin;
1	5	265000.00	confirmed	2026-04-08 11:03:52.797246
3	10	15000.00	confirmed	2026-04-08 11:44:05.064257
2	5	280000.00	confirmed	2026-04-08 11:08:28.236448
\.


--
-- Data for Name: product_images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product_images (id, product_id, image_url, image_order, created_at) FROM stdin;
2	1	/static/images/products/pacifier.jfif	1	2026-04-07 15:50:17.287905
3	1	/static/images/products/pacifier 2.jfif	2	2026-04-07 15:50:17.287905
4	1	/static/images/products/pacifier 3.jfif	3	2026-04-07 15:50:17.287905
5	6	/static/images/products/20260408_210049_BabylettoM23701HYHC-800x552TopSlider_1.webp	1	2026-04-08 21:00:49.581596
6	6	/static/images/products/20260408_210049_download.jfif	2	2026-04-08 21:00:49.581596
7	7	/static/images/products/20260408_210710_sma_formula_2.jpg	1	2026-04-08 21:07:10.426337
8	7	/static/images/products/20260408_210710_sma_formula.webp	2	2026-04-08 21:07:10.426337
9	7	/static/images/products/20260408_210710_sma_formula.webp	3	2026-04-08 21:07:10.426337
10	8	/static/images/products/20260408_211156_swaddle_3.jfif	1	2026-04-08 21:11:56.163994
11	8	/static/images/products/20260408_211156_swaddle_2.jfif	2	2026-04-08 21:11:56.163994
14	9	/static/images/products/20260408_214719_pampers_2.jpg	1	2026-04-08 21:47:19.911079
15	9	/static/images/products/20260408_214719_pampers_3.jfif	2	2026-04-08 21:47:19.911079
16	10	/static/images/products/20260408_215347_seat_trainer_3.webp	1	2026-04-08 21:53:47.228337
18	10	/static/images/products/20260408_215509_seat_trainer_3.webp	2	2026-04-08 21:55:09.930797
19	10	/static/images/products/20260408_215509_seat_trainer_1.jpg	3	2026-04-08 21:55:09.930797
20	11	/static/images/products/20260408_220121_silcone_feeding_set_2.webp	1	2026-04-08 22:01:21.265895
21	11	/static/images/products/20260408_220121_silcone_feeding_set_3.jpg	2	2026-04-08 22:01:21.265895
22	12	/static/images/products/20260408_220510_car_seat_3.jpg	1	2026-04-08 22:05:10.730521
23	12	/static/images/products/20260408_220510_car_seat_2.webp	2	2026-04-08 22:05:10.730521
24	12	/static/images/products/20260408_220510_car_seat.webp	3	2026-04-08 22:05:10.730521
25	13	/static/images/products/20260408_221031_stroller_3.jpeg	1	2026-04-08 22:10:31.333565
26	14	/static/images/products/20260408_221346_teethers_3.jpg	1	2026-04-08 22:13:46.187935
27	14	/static/images/products/20260408_221346_teethers_2.jpg	2	2026-04-08 22:13:46.187935
28	15	/static/images/products/20260408_221823_potty_1.jpg	1	2026-04-08 22:18:23.08536
29	15	/static/images/products/20260408_221823_potty_2.webp	2	2026-04-08 22:18:23.08536
30	15	/static/images/products/20260408_221823_potty_3.webp	3	2026-04-08 22:18:23.08536
31	16	/static/images/products/20260408_222507_bath_basin.webp	1	2026-04-08 22:25:07.883991
32	16	/static/images/products/20260408_222507_batj.webp	2	2026-04-08 22:25:07.883991
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, description, price, stock, image_url, category, action, discount) FROM stdin;
1	Pacifier	This is a very good product for keeping babies quiet.	15000.00	8	\N	Infant (0-6 Months)	On Sale	0.00
6	Baby Crib	This is a comfy easy to set up crib for 0-6 months babies	249999.98	5	\N	Infant (0-6 Months)	New Arrival	0.00
7	SMA Formula.	Powdered milk for babies 0-6 months.	50000.00	20	\N	Infant (0-6 Months)	On Sale	0.00
8	Swaddles	Mimicks womb and keeps baby warm and cozy.	80000.00	10	\N	Infant (0-6 Months)	Limited Edition	4.97
9	Pampers (Diapers & Wipes Combo) 	Diapers and Wipes combo discounted	102000.00	24	\N	Infant (0-6 Months)	Bestseller	10.00
10	Seat Trainer	This comfy seat trainer starts your baby on their sitting posture.	60000.00	9	\N	Sitter/Crawler (6-12 Months)	New Arrival	0.00
11	Silcone Feeding Set	This is for kids to learn how to feed	70000.00	23	\N	Toddler (12-18+ Months)	Bestseller	0.00
12	Car Seat	Protects your baby when driving.	800000.00	10	\N	Sitter/Crawler (6-12 Months)	On Sale	0.00
13	Baby Stroller	Push your baby around in comfort, replaceable wheels and easy set up.	1500000.00	7	\N	Sitter/Crawler (6-12 Months)	On Sale	10.00
14	Teethers	Teethers for toddlers.	17000.00	15	\N	Toddler (12-18+ Months)	On Sale	0.00
15	Toddler Potty 	This is a comfy potty toilet trainer for toddlers.	700000.00	5	\N	Toddler (12-18+ Months)	Limited Edition	0.00
16	Bath Basin	Bath basins for toddlers	30000.00	11	\N	Toddler (12-18+ Months)	On Sale	0.00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, name, email, password, role, created_at) FROM stdin;
2	John Doe	john@email.com	$2b$12$MlP5inv4RdgCbstk88Qb2O3VxE39s/IaFqslQT5ssG.qy0g397NLK	customer	2026-04-07 12:51:41.202894
1	Admin	admin@store.com	$2b$12$BNjrANdMxw9qlPCZyfWo9uKbCKgc0GhWz.Xj3mCT1OXxu4Y2v47RK	admin	2026-04-07 11:20:32.791683
5	Customer	customer@store.com	$2b$12$jycakbFJf8R5MIzuc5t8J.37hKs1lrzHOKW7wc/WWuhY0VE0lP6dO	customer	2026-04-07 14:15:39.113108
6	Test Customer	testuser1775635369@test.com	$2b$12$GDvE1D.o73ov/atirNEafuYvSURRYLlZnvNOQ94Ovcwmof.jkL9mm	customer	2026-04-08 11:02:49.572664
7	Test Customer	testuser1775635405@test.com	$2b$12$0sUYUn2d9Q55Hj6iW6qJdOUOea.UqDzkM/x5ZeQ/ot3limhuGKmIm	customer	2026-04-08 11:03:25.95203
8	Test Customer	testuser1775635429@test.com	$2b$12$.rUCWxIh4seY2xqREnmbR.ghpweb8bZbuLpBRnMmxKqhjKaKWx0M.	customer	2026-04-08 11:03:49.968059
9	Test Registration User	testuser_1775636834@example.com	$2b$12$iPeH0VL7PS0BhMSZ21Cl0uLCIFJ1Pp4xtkQTYHrVkFp1cqFepaTwm	customer	2026-04-08 11:27:14.771286
10	jonah vance	jonahvance@store.com	$2b$12$sgHMKTeWwtloTRjOZFdYwuMfpjkTEeecrgnLnDnkwqHrEIGQvXB/e	customer	2026-04-08 11:40:40.625425
\.


--
-- Name: cart_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cart_id_seq', 14, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_id_seq', 5, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_id_seq', 3, true);


--
-- Name: product_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_images_id_seq', 32, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 16, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 10, true);


--
-- Name: cart cart_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart
    ADD CONSTRAINT cart_pkey PRIMARY KEY (id);


--
-- Name: cart cart_user_id_product_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart
    ADD CONSTRAINT cart_user_id_product_id_key UNIQUE (user_id, product_id);


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
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_product_images_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_images_product_id ON public.product_images USING btree (product_id);


--
-- Name: cart cart_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart
    ADD CONSTRAINT cart_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: cart cart_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cart
    ADD CONSTRAINT cart_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


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
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict JCMgQWW91NIVobJIxq6uefTGcSALzZvlZsY3SkIGaf59oB4FExK246IbX3SeujN

