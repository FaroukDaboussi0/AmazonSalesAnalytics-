# Amazon Sales Rapport Data Warehouse Project

## Overview
The Amazon Sales Rapport Data Warehouse (DW) project aims to create a comprehensive data infrastructure for analyzing and reporting on sales data from Amazon. It involves building a robust data warehouse architecture, implementing Extract, Transform, Load (ETL) processes, and enabling visualization and forecasting capabilities.

## Project Components
1. **ETL Process**
   - **Extraction:** Data is extracted from various sources, including CSV and Excel files, using Python scripts.
   - **Transformation:** Extracted data undergoes transformation steps to ensure consistency, handle missing values, and prepare it for loading into the data warehouse.
   - **Loading:** Transformed data is loaded into the data warehouse tables, including the sales fact table and dimension tables for customers, products, dates, and geography.
   
2. **Data Warehouse Architecture**
   - The data warehouse architecture includes tables for storing sales data (fact table) and related dimensions such as date, geography, product, and customer.
   - Indexes are created to optimize query performance, ensuring efficient retrieval of data.
   ![Data Warehouse Architecture](/Captures/Sales_DW_architecture.jpg "Data Warehouse Architecture")
   
3. **Update Process**
   - The project implements a robust update process to maintain data integrity and consistency.
   - Existing data in the data warehouse is compared with new data to identify duplicates and update the warehouse accordingly.
   - Here is a helpful tool GUI for the ETL :
   ![ETL GUI](/Captures/GUI_ETL.png "ETL GUI")
4. **Visualization and Reporting**
   - After updating the data warehouse, visualization and reporting capabilities are enabled using Power BI.
   - Power BI is used to create reports and dashboards for analyzing sales trends and performance.
   ![Title Page](/Captures/Title_Page_BI.png "Title Page")
   ![Page of content](/Captures/Table_of_content.png "Page of content")
   ![Sales overview](/Captures/Sales_overview.png "Sales overview")
   ![Cutomer analysis](/Captures/Customer_Analysis.png "Cutomer analysis")
   ![Market Growth analysis](/Captures/Market_Growth_Analysis.png "Market Growth analysis")
   ![Product analysis](/Captures/Product_%20Analysis.png "Product analysis")

   
5. **Sales Forecasting**
   - The project integrates with R for sales forecasting.
   - Time series analysis and forecasting techniques are applied to predict future sales trends based on historical data.
   ![Sales Forecasting](/Captures/Sales_forecast.png "Sales Forecasting")

## How to Use
1. **Clone the Repository:** Clone this GitHub repository to your local machine.
2. **Install Dependencies:** Ensure you have Python, MySQL, and necessary Python packages installed. Additionally, Power BI Desktop is required.
3. **Install Required Packages:** Use `pip install -r requirements.txt` to install the necessary Python packages listed in the requirements.txt file.
4. **Run ETL Process:** Execute the Python scripts to perform the ETL process and update the data warehouse.
5. **Explore Data:** Utilize Power BI to explore and visualize the sales data stored in the data warehouse.
6. **Forecast Sales:** Utilize R for sales forecasting based on historical data.


This project is made by Farouk Daboussi .

Contributions to the project are welcome! Feel free to submit bug reports, feature requests, or pull requests.

## License
This project is licensed under the MIT License.
