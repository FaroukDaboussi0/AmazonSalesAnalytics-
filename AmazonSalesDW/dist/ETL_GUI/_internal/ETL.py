import os
import glob
import pandas as pd
import mysql.connector
import sys
import argparse
import gender_guesser.detector as gender
import pandas as pd 
import datetime
def extract_files(folder_path):
    # Find all CSV and XLS files in the directory
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    xls_files = glob.glob(os.path.join(folder_path, '*.xls')) + glob.glob(os.path.join(folder_path, '*.xlsx'))
    return csv_files + xls_files

def validate_structure(data, expected_columns):
    # Validate the structure of the data
    if list(data.columns) != expected_columns:
        raise ValueError("File structure does not match the expected schema")
    return data

def extract_data(file_path, expected_columns):
    # Extract data from CSV or XLS and validate its structure
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")
    return validate_structure(data, expected_columns)

def transform_data(data):
    # Drop columns with more than 2 NaN values
    data= data.drop(columns=["Postal Code","Row ID"])
    data = data.dropna(axis=1, thresh=len(data) - 2)
    
    # Fill remaining NaN values with mode if categorical or mean if numeric
    for column in data.columns:
        if data[column].dtype == 'object':  # Categorical data
            mode_value = data[column].mode()[0]
            data[column].fillna(mode_value, inplace=True)
        else:  # Numeric data
            mean_value = data[column].mean(skipna=True)
            data[column].fillna(mean_value, inplace=True)
    print(f"transfomed data nan number : {data.isna().sum()}")
    return data

def load_data(existing_data,all_data,new_data, sql_user, sql_host, sql_database):
    print(f"number of new data :{len(new_data)}")
    if len(new_data) != 0:
        try :
            print(new_data.isna().sum())
            print(f"first {list(new_data.columns)}")
            # Load only new data into MySQL database

            conn = mysql.connector.connect(user=sql_user, host=sql_host, database=sql_database)
            cursor = conn.cursor(buffered=True)
            insert_query = "INSERT INTO SA (Order_ID,Order_Date ,Ship_Date,	Ship_Mode,	Customer_ID,	Customer_Name,	Segment,	City,	State,	Country,	Region,	Market	,Product_ID,	Category,	Sub_Category,	Product_Name,	Sales,	Quantity,	Discount,	Profit,	Shipping_Cost,	Order_Priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # Convert DataFrame to a list of tuples
            list_of_tuples = [tuple(row) for row in new_data.itertuples(index=False)]
            print(f"number of inserted data : {len(list_of_tuples)}")
            # Execute the INSERT statement for each row of data
            for row in list_of_tuples:
                cursor.execute(insert_query, row)
            
            # Commit the changes
            conn.commit()
            print("SA loaded succefully")
            
            #Customer Update

            # Extraire les Customer_ID des deux DataFrames
            existing_customer_ids = set(existing_data['Customer_ID'])
            all_customer_ids = set(all_data['Customer ID'])

            # Trouver les nouveaux Customer_ID
            new_customer_ids = all_customer_ids - existing_customer_ids
            print(f"new_customer_ids : {len(new_customer_ids)}")
            # Filtrer les nouvelles lignes de all_data basées sur les nouveaux Customer_ID
            new_customers_data = all_data[all_data['Customer ID'].isin(new_customer_ids)]
            new_customers_data = new_customers_data.drop_duplicates(subset='Customer ID')
            insert_query_customer = """
            INSERT INTO customer (customer_id, customer_name, segment) 
            VALUES (%s, %s, %s)
            """

            # Convertir le DataFrame en une liste de tuples
            data_to_insert = [tuple(row) for row in new_customers_data[['Customer ID', 'Customer Name', 'Segment']].values]

            # Exécuter l'insertion pour chaque ligne

            cursor.executemany(insert_query_customer, data_to_insert)
            conn.commit()
            print("Data Customer inserted successfully")
            
            #Updating Product 
            existing_products_ids = set(existing_data['Product_ID'])
            all_products_ids = set(all_data['Product ID'])
            # Trouver les nouveaux Customer_ID
            new_products_ids = all_products_ids - existing_products_ids
            print(f"new_products_ids : {len(new_products_ids)}")
            # Filtrer les nouvelles lignes de all_data basées sur les nouveaux Customer_ID
            new_products_data = all_data[all_data['Product ID'].isin(new_products_ids)]
            new_products_data = new_products_data.drop_duplicates(subset='Product ID')
            insert_query_product = """
            INSERT INTO product (product_id, category, sub_category, product_name) 
            VALUES (%s, %s, %s,%s)
            """


            # Convertir le DataFrame en une liste de tuples
            data_to_insert = [tuple(row) for row in new_products_data[['Product ID', 'Category', 'Sub-Category','Product Name']].values]

            # Exécuter l'insertion pour chaque ligne

            cursor.executemany(insert_query_product, data_to_insert)
            conn.commit()
            print("Data product inserted successfully")
            
            #update geographique 
            existing_data['composite_key'] = existing_data['City']+ '_' + existing_data['State']+ '_' + existing_data['Country']+ '_' + existing_data['Region'] + '_' + existing_data['Market'] 
            all_data['composite_key'] = all_data['City']+ '_' + all_data['State']+ '_' + all_data['Country']+ '_' + all_data['Region'] + '_' + all_data['Market'] 

            # Afficher le nombre de lignes dans existing_order_ids
            existing_goeg_ids = existing_data['composite_key']
            print(f"How many rows exist in existing_order_ids: {len(existing_goeg_ids)}")

            # Identifier les lignes à supprimer
            rows_to_delete = all_data[all_data['composite_key'].isin(existing_goeg_ids)]
            print(f"Number of rows_to_delete: {len(rows_to_delete)}")

            # Supprimer les lignes identifiées de all_data
            geog_data = all_data[~all_data['composite_key'].isin(existing_goeg_ids)]
            geog_data = geog_data.drop_duplicates(subset='composite_key')
            # Supprimer la colonne composite_key si nécessaire
            all_data = all_data.drop(columns=['composite_key'])
            existing_data = existing_data.drop(columns=['composite_key'])
            geog_data = geog_data.drop(columns=['composite_key'])
            print(f"geog_data len = {len(geog_data)}")
            print(f"existing data len = {len(existing_data)}")
            insert_query_gegraphique = """
            INSERT INTO geographique (city,	state,	country, region, market) 
            VALUES (%s, %s, %s,%s,%s)
            """


            # Convertir le DataFrame en une liste de tuples
            data_to_insert = [tuple(row) for row in geog_data[['City', 'State', 'Country','Region','Market']].values]

            # Exécuter l'insertion pour chaque ligne

            cursor.executemany(insert_query_gegraphique, data_to_insert)
            conn.commit()
            print("Data Geographique inserted successfully")
        
            #updationg Dates



            # Extraire les Customer_ID des deux DataFrames
            existing_dates1_ids = set(existing_data['Order_Date'])
            all_dates1_ids = set(all_data['Order Date'])
            
            # Trouver les nouveaux Customer_ID
            new_dates1_ids = all_dates1_ids - existing_dates1_ids
            print(f"new_customer_ids : {len(new_dates1_ids)}")
            # Filtrer les nouvelles lignes de all_data basées sur les nouveaux Customer_ID
            new_dates1_data = all_data[all_data['Order Date'].isin(new_dates1_ids)]
            new_dates1_data = new_dates1_data.drop_duplicates(subset='Order Date')
            insert_query_date1 = """
            INSERT INTO date (date) 
            VALUES (%s)
            """

            # Convertir le DataFrame en une liste de tuples
            data_to_insert = [tuple(row) for row in new_dates1_data[['Order Date']].values]

            # Exécuter l'insertion pour chaque ligne

            cursor.executemany(insert_query_date1, data_to_insert)
            conn.commit()
            print("Data date1 inserted successfully")

            # Extraire les Customer_ID des deux DataFrames
            existing_dates2_ids = set(existing_data['Ship_Date'])
            all_dates2_ids = set(all_data['Ship Date'])
            
            # Trouver les nouveaux Customer_ID
            new_dates2_ids = all_dates2_ids - existing_dates2_ids
            print(f"new_date2_ids : {len(new_dates2_ids)}")
            # Filtrer les nouvelles lignes de all_data basées sur les nouveaux Customer_ID
            new_dates2_data = all_data[all_data['Ship Date'].isin(new_dates2_ids)]
            new_dates2_data = new_dates2_data.drop_duplicates(subset='Ship Date')
            insert_query_date2 = """
            INSERT INTO date (date) 
            VALUES (%s)
            """

            # Convertir le DataFrame en une liste de tuples
            data_to_insert = [tuple(row) for row in new_dates2_data[['Ship Date']].values]

            # Exécuter l'insertion pour chaque ligne

            cursor.executemany(insert_query_date2, data_to_insert)
            conn.commit()
            print("Data date2 inserted successfully")


            cursor = conn.cursor(buffered=True)
            get_date_query = "SELECT * FROM date WHERE year = 0"
            cursor.execute(get_date_query)
            daterow = [row for row in cursor.fetchall()]
            if len(daterow) !=0 :
                def extract_date_features(id, date_str):
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Using datetime.datetime.strptime
                    features = {
                        "id": id,
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "month": date_obj.month,
                        "year": date_obj.year,
                        "quarter": (date_obj.month - 1) // 3 + 1,
                        "day_of_week": date_obj.strftime("%A"),
                        "semester": (date_obj.month <= 6) and 1 or 2,
                        "is_weekend": date_obj.weekday() in [5, 6],
                        "is_holiday": False
                    }
                    return features
                processed_data = [extract_date_features(row[0], str(row[1])) for row in daterow]
                update_query = """
                    UPDATE date
                    SET month = %s, year = %s, quarter = %s, day_of_week = %s, semester = %s, is_weekend = %s, is_holiday = %s
                    WHERE id = %s  
                """
                print("error in insert date details")
                for row in processed_data:  
                    cursor.execute(update_query, (row["month"], row["year"], row["quarter"], row["day_of_week"], row["semester"], row["is_weekend"], row["is_holiday"], int(row["id"])))
                conn.commit()
            print("date details are updated")

            get_customer_query = "SELECT * FROM customer WHERE sex IS NULL"
            cursor.execute(get_customer_query)
            customer_data = [row for row in cursor.fetchall()]
            columns = [col[0] for col in cursor.description]
            customer_all_data = pd.DataFrame(customer_data, columns=columns)
            if not customer_all_data.empty:
                # Initialize the gender detector
                d = gender.Detector()

                # Define a function to predict gender
                def predict_gender(name):
                    first_name = name.split()[0]  # Assuming the first word is the first name
                    gender = d.get_gender(first_name)
                    
                    # Map gender-guesser output to Male/Female
                    if gender in ['male', 'mostly_male']:
                        return 'Male'
                    elif gender in ['female', 'mostly_female']:
                        return 'Female'
                    else:
                        return 'Other'

                new_df_customer = pd.DataFrame()
                columns_we_need = ["customer_id","customer_name"]
                new_df_customer[columns_we_need] = customer_all_data[columns_we_need]
                # Apply the function to the 'name' column and create a new 'sex' column
                new_df_customer['sex'] = new_df_customer["customer_name"].apply(predict_gender)
                print("done sex")
                values_to_update = [(row["sex"],row["customer_id"]) for index, row in new_df_customer.iterrows()]
                print(values_to_update[1])
                # Prepare SQL query for updating the table
                update_stmt = "UPDATE customer SET sex = %s WHERE customer_id = %s"
                print("sex updated")
                # Execute the update query for each tuple in the list
                cursor.executemany(update_stmt, values_to_update)
                conn.commit()
            
            print("sex updated")
            
            check_empty_lifespan = "SELECT * FROM customer Where lifespan_days IS NULL"
            cursor.execute(check_empty_lifespan)
            lifespan_data = [row for row in cursor.fetchall()]
            columns = [col[0] for col in cursor.description]
            lifespan_all_data = pd.DataFrame(lifespan_data, columns=columns)
            if not lifespan_all_data.empty :
                get_all_data_query = "SELECT * FROM sa"
                cursor.execute(get_all_data_query)
                get_all_data = [row for row in cursor.fetchall()]
                columns = [col[0] for col in cursor.description]
                sa_all_data = pd.DataFrame(get_all_data, columns=columns)
                sa_all_data['Order_Date'] = pd.to_datetime(sa_all_data['Order_Date'])

                # Group by Customer ID and calculate the lifespan
                customer_lifespan = sa_all_data.groupby('Customer_ID').agg(
                    First_Purchase=('Order_Date', 'min'),
                    Last_Purchase=('Order_Date', 'max')
                )

                # Calculate the lifespan in days
                customer_lifespan['Lifespan (days)'] = (customer_lifespan['Last_Purchase'] - customer_lifespan['First_Purchase']).dt.days

                # Reset the index to have Customer ID as a column
                customer_lifespan.reset_index(inplace=True)

                update_stmt = "UPDATE customer SET lifespan_days = %s WHERE customer_id = %s"
                print(f"processing insertion of lifespan_days number = {len(customer_lifespan)}")
                # Update the customer table in the database
                values_to_update = [(int(row['Lifespan (days)']),row['Customer_ID']) for index, row in customer_lifespan.iterrows()]
                cursor.executemany(update_stmt, values_to_update)
            print("customer lifespan days is updated")
            #TRUNCATE faitvente
            cursor.execute("TRUNCATE TABLE sales_dw.faitvente")
            conn.commit()

            #allimentation fait 

            alimentation_fait_query = """
                INSERT INTO sales_dw.faitvente 
                (Order_ID, Order_Date_ID, Ship_Date_ID, Ship_Mode, Customer_ID, geographique_ID, Product_ID, Sales, Quantity, Discount, Shipping_Cost, Order_Priority)
                SELECT 
                    sa.Order_ID, 
                    (SELECT id FROM sales_dw.date AS d_order WHERE d_order.date = sa.Order_Date LIMIT 1) AS Order_Date_ID, 
                    (SELECT id FROM sales_dw.date AS d_ship WHERE d_ship.date = sa.Ship_Date LIMIT 1) AS Ship_Date_ID, 
                    sa.Ship_Mode, 
                    c.id AS Customer_ID, 
                    g.id AS Geographique_ID, 
                    p.id AS Product_ID, 
                    sa.Sales, 
                    sa.Quantity, 
                    sa.Discount, 
                    sa.Shipping_cost, 
                    sa.Order_Priority
                FROM 
                    sales_dw.sa AS sa
                JOIN 
                    sales_dw.geographique AS g ON sa.city = g.city AND sa.state = g.state AND sa.country = g.country AND sa.region = g.region AND sa.market = g.market
                JOIN 
                    sales_dw.product AS p ON sa.Product_ID = p.product_id
                JOIN 
                    sales_dw.customer AS c ON sa.Customer_ID = c.customer_id
    """
            cursor.execute(alimentation_fait_query)
            # Commit the changes
            conn.commit()
            cursor.close()
            conn.close()
            print("fait is updated successfully")

        except Exception as e:
            print(f"Error occurred during insertion: {e}")
            conn.rollback()  # Rollback changes if an error occurs
        finally:
            cursor.close()
            conn.close()
    else : 
        print("the dw is already updated")

def extract_existing_data(sql_user, sql_host, sql_database):
    # Extract existing data from MySQL database
    conn = mysql.connector.connect(user=sql_user, host=sql_host, database=sql_database)
    query = "SELECT * FROM SA"
    cursor = conn.cursor(buffered=True)  
    cursor.execute(query)
    existing_data = [row for row in cursor.fetchall()]
    conn.close()
    columns = [col[0] for col in cursor.description]
    existing_df = pd.DataFrame(existing_data, columns=columns)
    return existing_df

def main():
    parser = argparse.ArgumentParser(description='ETL Process')
    parser.add_argument('folder_path', help='Path to the folder containing input data files (CSV or XLS)')
    parser.add_argument('sql_user', help='SQL username')
    parser.add_argument('sql_host', help='SQL host')
    parser.add_argument('sql_database', help='SQL database name')
    args = parser.parse_args()

    # Define the expected structure
    expected_columns = ['Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment','Postal Code', 'City', 'State', 'Country', 'Region', 'Market', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Sales', 'Quantity', 'Discount', 'Profit', 'Shipping Cost', 'Order Priority']  

    try:
        # Extract existing data from DW
        existing_data = extract_existing_data(args.sql_user, args.sql_host, args.sql_database)
        existing_data = existing_data.drop(columns="Row_ID")
        files = extract_files(args.folder_path)
        all_data = pd.DataFrame()

        # Extract, validate, and transform each file
        for file_path in files:
            data = extract_data(file_path, expected_columns)
            transformed_data = transform_data(data)
            all_data = pd.concat([all_data, transformed_data], ignore_index=True)
        print(f"all_data first : {print(all_data.isna().sum())} " )
        print(f"number of rows must be grater than 51000 = {len(all_data)}")
        # Remove duplicate rows within the new data
        all_data.drop_duplicates(subset=['Order ID', 'Product ID'], inplace=True)
        print(f"all_data drop diplicated : {print(all_data.isna().sum())} " )
        print(f"number of rows must be 51 000 = {len(all_data)}")
        print(f"columns name of existing_data :{existing_data.columns}")
        # Créer des clés composites pour la comparaison
        existing_data['composite_key'] = existing_data['Order_ID'] + '_' + existing_data['Product_ID']
        all_data['composite_key'] = all_data['Order ID'] + '_' + all_data['Product ID']

        # Afficher le nombre de lignes dans existing_order_ids
        existing_order_ids = existing_data['composite_key']
        print(f"How many rows exist in existing_order_ids: {len(existing_order_ids)}")

        # Identifier les lignes à supprimer
        rows_to_delete = all_data[all_data['composite_key'].isin(existing_order_ids)]
        print(f"Number of rows_to_delete: {len(rows_to_delete)}")

        # Supprimer les lignes identifiées de all_data
        new_data = all_data[~all_data['composite_key'].isin(existing_order_ids)]

        # Supprimer la colonne composite_key si nécessaire
        new_data = new_data.drop(columns=['composite_key'])
        existing_data = existing_data.drop(columns=['composite_key'])
        # Vérifier le résultat final
        print(f"Number of rows in new_data: {len(new_data)}")

        print(f"all_data second : {print(all_data.isna().sum())}  , count of new data : {len(new_data)}" )
        # Load the new data into the database
        load_data(existing_data,all_data,new_data, args.sql_user, args.sql_host, args.sql_database)
        print("Done")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
