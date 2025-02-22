## config.py
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


DATABASE_SCHEMA = """-- Core Tables
Table customer {
  customer_id int [pk]
  store_id int
  first_name text
  last_name text
  email text
  address_id int
  activebool boolean
  create_date date
  last_update timestamp with time zone
  active integer
}


Table film_actor {
  actor_id int
  film_id int
  last_update timestamp with time zone
}

Table film_category {
  film_id int [pk]
  category_id int
  last_update timestamp with time zone
}

Table inventory {
  inventory_id int [pk]
  film_id int
  store_id int
  last_update timestamp with time zone
}

Table staff {
  staff_id int [pk]
  first_name text
  last_name text
  address_id int
  email text
  store_id int
  active boolean
  username text
  password text
  last_update timestamp with time zone
  picture bytea
}


Table rental {
  rental_id int [pk]
  rental_date timestamp with time zone
  inventory_id int
  customer_id int
  return_date timestamp with time zone
  staff_id int
  last_update timestamp with time zone
}

--------------------------------

Table actor {
  actor_id int [pk]
  first_name text
  last_name text
  last_update timestamp with time zone
}

Table category {
  category_id int [pk]
  name text
  last_update timestamp with time zone
}

Table film {
  film_id int [pk]
  title text
  description text
  release_year int
  language_id int
  original_language_id int
  rental_duration int
  rental_rate decimal(4,2)
  length smallint
  replacement_cost decimal(5,2)
  rating mpaa_rating  // (G, PG, PG-13, R, NC-17)
  last_update timestamp with time zone
  special_features text[]
  fulltext tsvector
}


Table store {
  store_id int [pk]
  manager_staff_id int
  address_id int
  last_update timestamp with time zone
}


--------------------------------

Table language {
  language_id int [pk]
  name text
  last_update timestamp with time zone
}   

Table address {
  address_id int [pk]
  address text
  address2 text
  district text
  city_id int
  postal_code text
  phone text
  last_update timestamp with time zone
}

Table city {
  city_id int [pk]
  city text
  country_id int
  last_update timestamp with time zone
}   

Table country {
  country_id int [pk]
  country text
  last_update timestamp with time zone
}   
    

--------------------------------
# Not dependent on any other table

Table dummy_category {
  category_id int [pk]
  name text
  last_update timestamp with time zone
}

Table payment {
  payment_id int [pk]
  customer_id int
  staff_id int
  rental_id int
  amount decimal(5,2)
  payment_date timestamp with time zone
}






-- Key Relationships

-- Address Hierarchy
Ref: address.city_id > city.city_id
Ref: city.country_id > country.country_id

-- Film Related
Ref: film.language_id > language.language_id
Ref: film.original_language_id > language.language_id

-- Film Categorization and Actors
Ref: film_actor.film_id > film.film_id
Ref: film_actor.actor_id > actor.actor_id
Ref: film_category.film_id > film.film_id
Ref: film_category.category_id > category.category_id

-- Store and Staff
Ref: store.manager_staff_id > staff.staff_id
Ref: store.address_id > address.address_id
Ref: staff.store_id > store.store_id
Ref: staff.address_id > address.address_id

-- Customer
Ref: customer.store_id > store.store_id
Ref: customer.address_id > address.address_id

-- Inventory
Ref: inventory.film_id > film.film_id
Ref: inventory.store_id > store.store_id

-- Rental
Ref: rental.inventory_id > inventory.inventory_id
Ref: rental.customer_id > customer.customer_id
Ref: rental.staff_id > staff.staff_id

-- Payment
Ref: payment.rental_id > rental.rental_id
Ref: payment.customer_id > customer.customer_id
Ref: payment.staff_id > staff.staff_id"""
