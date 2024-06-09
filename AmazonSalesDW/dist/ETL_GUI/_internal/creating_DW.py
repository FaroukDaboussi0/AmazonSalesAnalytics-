import mysql.connector
import argparse

def execute_query(cursor, query, multi=False):
    try:
        if multi:
            for result in cursor.execute(query, multi=True):
                if result.with_rows:
                    result.fetchall()
        else:
            cursor.execute(query)
            if cursor.with_rows:
                cursor.fetchall()
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cnx.rollback()
        # Clear any unread results
        if cursor.with_rows:
            cursor.fetchall()

# Argument parsing
parser = argparse.ArgumentParser(description='Process some SQL connection parameters.')
parser.add_argument('sql_user', type=str, help='SQL username')
parser.add_argument('sql_host', type=str, help='SQL host')
parser.add_argument('sql_database', type=str, help='SQL database name')

args = parser.parse_args()

# Connect to the database
cnx = mysql.connector.connect(user=args.sql_user, password='', host=args.sql_host)
cursor = cnx.cursor()

# Check if the database exists
cursor.execute(f"SHOW DATABASES LIKE '{args.sql_database}'")
result = cursor.fetchone()

if result:
    print(f"{args.sql_database} already exists")
else:
    # Create the database
    create_database_query = f"CREATE DATABASE IF NOT EXISTS {args.sql_database}"
    execute_query(cursor, create_database_query)
    cnx.commit()

    # Use the newly created database
    use_database_query = f"USE {args.sql_database}"
    execute_query(cursor, use_database_query)
    cnx.commit()
    
    table_name = "SA"

    # Define table structure (outside the cursor.execute)
    table_schema = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
      Row_ID INT AUTO_INCREMENT PRIMARY KEY,
      Order_ID VARCHAR(255),
      Order_Date DATETIME,
      Ship_Date DATETIME,
      Ship_Mode VARCHAR(255),
      Customer_ID VARCHAR(255),
      Customer_Name VARCHAR(255),
      Segment VARCHAR(255),
      City VARCHAR(255),
      State VARCHAR(255),
      Country VARCHAR(255),
      Region VARCHAR(255),
      Market VARCHAR(255),
      Product_ID VARCHAR(255),
      Category VARCHAR(255),
      Sub_Category VARCHAR(255),
      Product_Name VARCHAR(255),
      Sales DECIMAL(10,2),
      Quantity INT,
      Discount DECIMAL(5,2),
      Profit DECIMAL(10,2),
      Shipping_Cost DECIMAL(10,2),
      Order_Priority VARCHAR(255)
    )
    """

    # Try creating the table (optional, can be combined with data insertion)
    execute_query(cursor, table_schema)
    cnx.commit()

    # Date Dimension
    data_table_query = """
    CREATE OR REPLACE TABLE date (
      id INT PRIMARY KEY AUTO_INCREMENT,
      date DATE NOT NULL,
      month INT NOT NULL,
      year INT NOT NULL,
      quarter INT NOT NULL,
      semester INT NOT NULL,
      is_weekend BOOLEAN NOT NULL,
      is_holiday BOOLEAN NOT NULL,
      day_of_week VARCHAR(20) NOT NULL
    );
    """

    # Geographic Dimension
    geographique_table_query = """
    CREATE OR REPLACE TABLE geographique (
      id INT PRIMARY KEY AUTO_INCREMENT,
      city VARCHAR(50) NOT NULL,
      state VARCHAR(50) NOT NULL,
      country VARCHAR(50) NOT NULL,
      region VARCHAR(50) NOT NULL,
      market VARCHAR(50) NOT NULL
    );
    """

    # Product Dimension
    product_table_query = """
    CREATE OR REPLACE TABLE product (
      id INT PRIMARY KEY AUTO_INCREMENT,
      product_id VARCHAR(20) NOT NULL,  -- Consider using the original ID
      category VARCHAR(50) NOT NULL,
      sub_category VARCHAR(50) NOT NULL,
      product_name VARCHAR(255) NOT NULL
    );
    """

    # Customer Dimension
    customer_table_query = """
    CREATE OR REPLACE TABLE customer (
      id INT PRIMARY KEY AUTO_INCREMENT,
      customer_id VARCHAR(20) NOT NULL,  -- Consider using the original ID
      customer_name VARCHAR(255) NOT NULL,
      segment VARCHAR(50) NOT NULL,
      sex VARCHAR(10),
      lifespan_days INT
    );
    """

    # Execute the queries
    execute_query(cursor, data_table_query)
    execute_query(cursor, geographique_table_query)
    execute_query(cursor, product_table_query)
    execute_query(cursor, customer_table_query)
    cnx.commit()

    fait_table_creation_query = """
    CREATE TABLE faitvente (
      id INT PRIMARY KEY AUTO_INCREMENT,
      Order_ID VARCHAR(20) NOT NULL, 
      Order_Date_ID INT NOT NULL, 
      Ship_Date_ID INT NOT NULL, 
      Ship_Mode VARCHAR(50) NOT NULL,
      Customer_ID INT NOT NULL,
      Geographique_ID INT NOT NULL,
      Product_ID INT NOT NULL,
      Sales DECIMAL(10,2) NOT NULL,
      Quantity INT NOT NULL,
      Discount DECIMAL(10,2) NOT NULL,
      Shipping_Cost DECIMAL(10,2) NOT NULL,
      Order_Priority VARCHAR(50) NOT NULL,
      FOREIGN KEY (Order_Date_ID) REFERENCES date(id),
      FOREIGN KEY (Ship_Date_ID) REFERENCES date(id),
      FOREIGN KEY (Customer_ID) REFERENCES customer(id),
      FOREIGN KEY (Geographique_ID) REFERENCES geographique(id),
      FOREIGN KEY (Product_ID) REFERENCES product(id)
    );
    """
    execute_query(cursor, fait_table_creation_query)
    cnx.commit()

    # Execute index creation queries
    index_queries = [
        "CREATE INDEX idx_product_Product_ID ON sales_dw.product (product_id);",
        "CREATE INDEX idx_customer_customer_id ON sales_dw.customer (customer_id);",
        "CREATE INDEX idx_date_date ON sales_dw.date (date);",
        "CREATE INDEX idx_geographique ON sales_dw.geographique(city, state, country, region, market);",
        "CREATE INDEX idx_sa_Order_Date ON sales_dw.sa (Order_Date);",
        "CREATE INDEX idx_sa_Ship_Date ON sales_dw.sa (Ship_Date);",
        "CREATE INDEX idx_customer_id ON sales_dw.sa (Customer_ID);"
    ]

    # Execute each index creation query separately
    for query in index_queries:
        execute_query(cursor, query)

    print("Data warehouse created successfully!") 

# Close the cursor and the connection
cursor.close()
cnx.close()
