## config.py
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

COT_TEXT2SQL_EXAMPLE = """**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany?
    **Evidence**: Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name
    = 'san pablo ave' AND T1.city = 'albany'
    **Query Plan**:
    ** Preparation Steps:**
    1. Initialize the process: Start preparing to execute the query.
    2. Prepare storage: Set up storage space (registers) to hold temporary results, initializing them to NULL.
    3. Open the location table: Open the location table so we can read from it.
    4. Open the generalinfo table: Open the generalinfo table so we can read from it.
    ** Matching Restaurants:**
    1. Start reading the location table: Move to the first row in the location table.
    2. Check if the street matches: Look at the street_name column of the current row in location. If it's not
    "san pablo ave," skip this row.
    3. Identify the matching row: Store the identifier (row ID) of this location entry.
    4. Find the corresponding row in generalinfo: Use the row ID from location to directly find the matching
    row in generalinfo.
    5. Check if the food type matches: Look at the food_type column in generalinfo. If it's not "thai," skip
    this row.
    6. Check if the city matches: Look at the city column in generalinfo. If it's not "albany," skip this row.
    ** Counting Restaurants:**
    1. Prepare to count this match: If all checks pass, prepare to include this row in the final count.
    2. Count this match: Increment the count for each row that meets all the criteria.
    3. Move to the next row in location: Go back to the location table and move to the next row, repeating
    the process until all rows are checked.
    4. Finalize the count: Once all rows have been checked, finalize the count of matching rows.
    5. Prepare the result: Copy the final count to prepare it for output.
    ** Delivering the Result:**
    1. Output the result: Output the final count, which is the number of restaurants that match all the
    specified criteria.
    2. End the process: Stop the query execution process.
    3. Setup phase: Before starting the actual query execution, the system prepares the specific values it will
    be looking for, like "san pablo ave," "thai," and "albany."
    **Final Optimized SQL Query:**
    SELECT COUNT(T1.id_restaurant) FROM generalinfo AS T1 INNER JOIN location AS T2
    ON T1.id_restaurant = T2.id_restaurant WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND
    T2.street_name = 'san pablo ave' 

"""

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
