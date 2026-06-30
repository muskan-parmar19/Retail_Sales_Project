
import pandas as pd
import numpy as np
import sqlite3


# Task 1: Data Ingestion
def run_pipeline():
    final_df = None

    try:
        #1. Load CSV files
        sales = pd.read_csv("data/sales_data.csv")
        products = pd.read_csv("data/products.csv")
        stores = pd.read_csv("data/Stores.csv")

        # Print Shapes
        print("Sales Data Shape:", sales.shape)
        print("Products Data Shape:", products.shape)
        print("Stores Data Shape:", stores.shape)

        # First 5 rows
        print("\nSales Data")
        print(sales.head())

        print("\nProducts Data")
        print(products.head())

        print("\nStores Data")
        print(stores.head())

        # 2.Missing values
        print("\nMissing Values in Sales Data")
        print(sales.isnull().sum())

        print("\nMissing Values in Products Data")
        print(products.isnull().sum())

        print("\nMissing Values in Stores Data")
        print(stores.isnull().sum())

       
        # Task 2: Data Cleaning
        #3.Remove duplicates
        before_sales = sales.shape[0]

        sales.drop_duplicates(inplace=True)

        after_sales = sales.shape[0]
        removed_sales = before_sales - after_sales

        print("Duplicate rows found in sales:", removed_sales)
        print("Duplicate rows removed in sales:", removed_sales)
        print("Rows before removing duplicates:", before_sales)
        print("Rows after removing duplicates:", after_sales)

        # 4. Fill missing quantity values
        sales["quantity"] = sales["quantity"].fillna(0)

        before = sales.shape[0]

        # Drop rows where amount is missing
        sales.dropna(subset=["amount"], inplace=True)

        after = sales.shape[0]

        print("Rows removed due to missing amount:", before - after)

        # Convert data types
        sales["sale_date"] = pd.to_datetime(
            sales["sale_date"],
            format="%d-%m-%Y",
            errors="coerce"
        )

        sales["amount"] = sales["amount"].astype(float)

        print("Cleaned DataFrame Shape:", sales.shape)

        # Additional cleaning for stores
        stores["city"] = stores["city"].fillna("Unknown")
        stores["region"] = stores["region"].fillna("Unknown")
        stores["store_name"] = stores["store_name"].fillna("Unknown")

       
        # Task 3: Data Transformation
       #6. Merge DataFrames
        merged_df = pd.merge(
            sales,
            products,
            on="product_id",
            how="inner"
        )

        final_df = pd.merge(
            merged_df,
            stores,
            on="store_id",
            how="inner"
        )

        print("\nMerged Data:")
        print(final_df.head())

        # Fill missing prices
        final_df["price"] = final_df["price"].fillna(0)


        # 7.Create total revenue column
        final_df["total_revenue"] = (
            final_df["quantity"] * final_df["price"]
        )

        print(final_df.head())

        # Revenue statistics
        print("Mean Revenue:",
              np.nanmean(final_df["total_revenue"]))

        print("Maximum Revenue:",
              np.max(final_df["total_revenue"]))

        print("Minimum Revenue:",
              np.min(final_df["total_revenue"]))

        #8. Revenue by city
        city_revenue = (
            final_df.groupby("city")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        print("\nRevenue by City:")
        print(city_revenue)

        
        # Task 4: Data Loading
        #9. Load into SQLite database
        conn = sqlite3.connect("retail_sales.db")

        final_df.to_sql(
            "retail_sales",
            conn,
            if_exists="replace",
            index=False
        )

        conn.close()

        print("\nData loaded successfully into retail_sales table.")

        # 10.Top 3 products
        conn = sqlite3.connect("retail_sales.db")

        query = """
        SELECT
            product_name,
            SUM(quantity) AS total_quantity_sold
        FROM retail_sales
        GROUP BY product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 3;
        """

        top_products = pd.read_sql(query, conn)

        print("\nTop 3 Products:")
        print(top_products)

        conn.close()

        
        # Task 5: Reporting & insights
       #11. Revenue per store per day
        conn = sqlite3.connect("retail_sales.db")

        query = """
        SELECT
            store_id,
            sale_date,
            SUM(total_revenue) AS total_revenue
        FROM retail_sales
        GROUP BY store_id, sale_date
        ORDER BY sale_date, store_id;
        """

        result = pd.read_sql(query, conn)

        print("\nRevenue Per Store Per Day:")
        print(result)

        conn.close()

        # 12.Summary report
        total_transactions = len(final_df)

        total_revenue = final_df["total_revenue"].sum()

        top_city = (
            final_df.groupby("city")["total_revenue"]
            .sum()
            .idxmax()
        )

        top_product = (
            final_df.groupby("product_name")["total_revenue"]
            .sum()
            .idxmax()
        )

        print("\n===== SUMMARY REPORT =====")
        print("Total Number of Transactions:",
              total_transactions)

        print("Total Revenue:",
              total_revenue)

        print("Top Selling City:",
              top_city)

        print("Top Selling Product:",
              top_product)

        print("\nFinal Data:")
        print(final_df.head())

        print("\nPipeline executed successfully.")

        return final_df
    
    #task 6: pipeline and error handling
    # 13. Error Handling
    except FileNotFoundError as e:
        print("Error: File not found")
        print(e)

    except KeyError as e:
        print(f"Error: Missing column {e}")

    except sqlite3.Error as e:
        print("Database error:")
        print(e)

    except Exception as e:
        print("An unexpected error occurred:")
        print(e)

    return None



df = run_pipeline()