-- create dot table
CREATE TABLE invoice_detail (
	supplier_name VARCHAR,
	product_line_number VARCHAR,
	product_line_desc VARCHAR,
	buying_group_number INT,
	buying_group_name VARCHAR,
	customer_num VARCHAR,
	customer_name VARCHAR,
	customer_shipping_city VARCHAR,
	customer_shipping_state VARCHAR,
	customer_shipping_zip VARCHAR,
	customer_invoice_number VARCHAR,
	invoice_date DATE,
	customer_po_number VARCHAR,
	customer_order_number VARCHAR,
	prod_dot_number VARCHAR,
	prod_mfg_number VARCHAR,
	item_upc VARCHAR,
	item_full_desc VARCHAR,
	qty_ordered INT,
	qty_received INT,
	dollars DECIMAL,
	cust_ext_gross_weight DECIMAL,
	cust_ext_net_weight DECIMAL,
	channel_num INT,
	channel_desc VARCHAR,
	segment_code INT,
	segment_desc VARCHAR,
	tier_num INT,
	tier_desc VARCHAR,
	prod_line_sub_cat VARCHAR,
	dot_dc VARCHAR
);

--- imported initial data (dot invoice detail 2016-2023)

-- create dot table

CREATE TABLE invoice_clean (
	month VARCHAR,
	year INT,
	customer_name VARCHAR,
	supplier_name VARCHAR,
	product_line_number VARCHAR,
	product_line_desc VARCHAR,
	buying_group_number INT,
	buying_group_name VARCHAR,
	customer_num VARCHAR,
	customer_shipping_city VARCHAR,
	customer_shipping_state VARCHAR,
	customer_shipping_zip VARCHAR,
	customer_invoice_number VARCHAR,
	invoice_date DATE,
	customer_po_number VARCHAR,
	customer_order_number VARCHAR,
	prod_dot_number VARCHAR,
	prod_mfg_number VARCHAR,
	item_upc VARCHAR,
	item_full_desc VARCHAR,
	qty_ordered INT,
	qty_received INT,
	dollars DECIMAL,
	cust_ext_gross_weight DECIMAL,
	cust_ext_net_weight DECIMAL,
	channel_num INT,
	channel_desc VARCHAR,
	segment_code INT,
	segment_desc VARCHAR,
	tier_num INT,
	tier_desc VARCHAR,
	prod_line_sub_cat VARCHAR,
	dot_dc VARCHAR,
	sale_origin VARCHAR,
	parent_customer VARCHAR,
	market_segment VARCHAR
);

select * from invoice_clean
order by invoice_date desc;

select * from unleashed_raw
order by completed_date desc;

select * from unleashed_clean
order by completed_date desc;

CREATE TABLE unleashed_raw (
	order_num VARCHAR,
	order_date DATE,
	req_date DATE,
	completed_date DATE,
	warehouse VARCHAR,
	customer_name VARCHAR,
	customer_type VARCHAR,
	product VARCHAR,
	product_group VARCHAR,
	status VARCHAR,
	quantity DECIMAL,
	sub_total DECIMAL);
	
CREATE TABLE unleashed_clean (
	month VARCHAR,
	year INT,
	completed_date DATE,
	customer_name VARCHAR,
	product VARCHAR,
	quantity DECIMAL,
	sub_total DECIMAL,
	usd DECIMAL,
	sale_origin VARCHAR,
	market_segment VARCHAR
	parent_customer VARCHAR);