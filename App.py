import streamlit as st
import mysql.connector
import pandas as pd
import time 

# MySQL connection
conn = mysql.connector.connect(
    host="autorack.proxy.rlwy.net",
    user="root",
    password="nmdmuwqNTEPwgrhBsWKShirIbToLflrU",
    database="railway",
    port=12064
)


cursor = conn.cursor()

menu = ("Home","Add Product","Add Production","Add Sales","Inventory")
choice = st.sidebar.selectbox("Navigation",menu)
#---------------------- Page Title ---------------

st.title("Production & Inventory Management")
st.write("Dashboard")
if choice == "Home":
    st.write("Welcome to the Production Inventory App")

    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            IFNULL(SUM(pr.quantity), 0) AS Total_Production,
            IFNULL(SUM(s.quantity), 0) AS Total_Sales,
            IFNULL(SUM(pr.quantity), 0) - IFNULL(SUM(s.quantity), 0) AS Remaining_Stock
        FROM products p
        LEFT JOIN production pr ON p.product_id = pr.product_id
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id, p.product_name
    """)
    dashboard_data = cursor.fetchall()

    if dashboard_data:
        df = pd.DataFrame(
            dashboard_data,
            columns=["Product ID", "Product Name", "Total Production", "Total Sales", "Remaining Stock"]
        )

        total_products = df["Product ID"].nunique()
        total_production = df["Total Production"].sum()
        total_sales = df["Total Sales"].sum()
        total_stock = df["Remaining Stock"].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Products", total_products)
        col2.metric("Total Production", total_production)
        col3.metric("Total Sales", total_sales)
        col4.metric("Remaining Stock", total_stock)

        st.subheader("Production by Product")
        st.bar_chart(df.set_index("Product Name")["Total Production"])

        st.subheader("Sales by Product")
        st.bar_chart(df.set_index("Product Name")["Total Sales"])

        st.subheader("Remaining Stock by Product")
        st.bar_chart(df.set_index("Product Name")["Remaining Stock"])

        st.subheader("Low Stock Products")
        low_stock_df = df[df["Remaining Stock"] < 10]

        if not low_stock_df.empty:
            st.dataframe(low_stock_df, use_container_width=True)
        else:
            st.success("No low stock products")

    else:
        st.warning("No dashboard data available")

# ---------------- ADD PRODUCT ----------------
elif choice == "Add Product":
    st.header("Add New Product")

    product_id = st.number_input("Product ID", min_value=0)
    product_name = st.text_input("Product Name")
    category = st.text_input("Category")

    if st.button("Save Product"):
        cursor.execute(
            "INSERT INTO products (product_id, product_name, category) VALUES (%s, %s, %s)",
            (product_id, product_name, category)
        )
        conn.commit()
        st.success("Product saved successfully!")
        time.sleep(2)
        st.rerun()

    #-------------- SHOW TABLE----------------------
    st.subheader("Products Table")
    cursor.execute("Select product_id,product_name,category from products")
    products_record = cursor.fetchall()
    if products_record:
        df = pd.DataFrame(products_record,columns=["product_id","product_name","category"])
        st.dataframe(df)


#---------------- Edit product data -------------------
    st.subheader("Edit Product Data")
    Edit_id = st.number_input("Enter Product Id to Edit",min_value=1)
    New_Product_Name = st.text_input("Enter New Product Name")
    New_Category = st.text_input("Enetr New Category")
    if st.button("Update Products Data"):
        cursor.execute("update products set product_name = %s,Category = %s where product_id = %s",(New_Product_Name,New_Category,Edit_id))
        conn.commit()
        if cursor._rowcount == 0:
            st.warning("No Data Found In This Id")
        else:
            st.success("Upadte successfully!")
            time.sleep(2)
            st.rerun()
            
           


        
#----------------- Delete Products Data -------------
    st.subheader("Delete Products Data")
    delete_id = st.number_input("Enter Delete Product Id",min_value=1)
    
    if st.button("Delete Product"):
        cursor.execute("delete from  products where Product_id = %s ",( delete_id,))
        conn.commit()
        if cursor.rowcount == 0:
            st.warning("No product found with this ID")
         
        else:
            st.success("Delete Successfully")
            time.sleep(2)
            st.rerun()
       
    
# ---------------- PRODUCTION ENTRY ----------------
elif choice == " Add Production":
    st.header("Enter Production Data")

    cursor.execute("SELECT product_id, product_name FROM products")
    product_data = cursor.fetchall()

    if product_data:
        product_dict = {name: pid for pid, name in product_data}

        product_name = st.selectbox("Select Product", list(product_dict.keys()))
        product_id = product_dict[product_name]

        production_date = st.date_input("Production Date")
        quantity = st.number_input("Production Quantity", min_value=1)

        if st.button("Save Production"):
            cursor.execute(
                "INSERT INTO production (product_id, production_date, quantity) VALUES (%s, %s, %s)",
                (product_id, production_date, quantity)
            )
            conn.commit()
            st.success("Production data saved successfully!")
    else:
        st.warning("Please add products first.")
        time.sleep(2)
        st.rerun()


#----------------SHOW TABLE ------------------
    st.subheader("Production Data")
    cursor.execute("select product_id, production_date, quantity from production")
    production_record = cursor.fetchall()
    if product_data:
        df= pd.DataFrame(production_record, columns=["product_id", "production_date", "quantity"])
        st.dataframe(df)

#--------------- EDIT PRODUCTION DATA --------------
    st.subheader("Update Production Data")
    Edit_id = st.number_input("Enetr Product Id To Edit",min_value=1)
    New_Quantity = st.number_input("Enter New Quantity",min_value=1)
    if st.button("Update Production Data"):
        cursor.execute("update production set Quantity = %s where product_id = %s", (New_Quantity,Edit_id))
        conn.commit()
        if cursor.rowcount ==0:
            st.warning("No Data Found In This Id")
        else:
            st.success("Upadte Successfully!")
            time.sleep(2)
            st.rerun()
        
   
#---------------- Delete Production Data -----------
    st.subheader("Delete Production Data")
    delete_id = st.number_input("Enter Delete Production Id ",min_value=0)
    if st.button("Delete Production Data"):
        cursor.execute("delete from production where production Id = %s",(delete_id,))
        conn.commit()
        if cursor.rowcount == 0:
            st.warning("No Data Found With This Id")
        else:
            st.success("Delete Successfully")
            time.sleep(2)
            st.rerun()

# ---------------- SALES ENTRY ----------------
elif choice == "Add gitSales":
    st.header("Enter Sales Data")
    
    cursor.execute("select product_id,product_name from products")
    product_data= cursor.fetchall()

    if product_data:
        product_dict = {name:pid for pid, name in product_data}

        product_name = st.selectbox("select product", list(product_dict.keys()))
        product_id = product_dict[product_name]

        sales_date = st.date_input("Sales Date")
        quantity = st.number_input("sales Quantity", min_value=1)
        if st.button("Save sales"):
            cursor.execute(
                "insert into sales(product_id,sales_date,quantity) values (%s, %s, %s)",
                (product_id,sales_date,quantity)
            )
            conn.commit()
            st.success("sales data saved successfully!")
    else:
        st.warning("Please add sales.")
        time.sleep(2)
        st.rerun()



#---------------- SHOW TABLE ---------------

    st.subheader("Sales Data")
    cursor.execute("select product_id,sales_date,quantity from sales")
    sales_record = cursor.fetchall()
    if sales_record:
        df = pd.DataFrame(sales_record,columns=["product_id","sales_date","quantity"])
        st.dataframe(df)

# -------------- EDIT SALES ---------------
    st.subheader("Edit Sales Data")
    Edit_id = st.number_input("Enter Sales Product Id",min_value=1)
    New_Quantity = st.number_input("Enetr New Quantity",min_value=1)
    if st.button("Update Data"):
        cursor.execute("update sales set Quantity = %s where Product_id = %s",(New_Quantity,Edit_id))
        conn.commit()
        if cursor.rowcount==0:
            st.warning("No Product Found in This Id")
        else:
            st.success("Upadte Successfully")
            time.sleep(2)
            st.rerun()
           
#--------------- Delete Sales Data ---------
    st.subheader("Delete Sales Data")
    delete_id = st.number_input("Enter Sales Data ID ",min_value=0)
    if st.button("Delete Sales data"):
        cursor.execute("delete from sales where sales_id = %s", (delete_id,))
        conn.commit()

        if cursor.rowcount ==0:
            st.warning("Enter Sales_Id Data Not Found")
        else:
            st.success("Delete Successfully")
            time.sleep(2)
            st.rerun()
# ---------------- INVENTORY ----------------
elif choice == "Inventory":
    st.header("Inventory Status")

    st.subheader("Search Box")
    Enter_Product_id = st.number_input("Enter Product Id", min_value=1)

    query = """
        SELECT
            p.product_id,
            p.product_name,
            IFNULL(SUM(pr.quantity), 0) AS Total_Production,
            IFNULL(SUM(s.quantity), 0) AS Total_Sales,
            IFNULL(SUM(pr.quantity), 0) - IFNULL(SUM(s.quantity), 0) AS stock
        FROM products p
        LEFT JOIN production pr ON p.product_id = pr.product_id
        LEFT JOIN sales s ON s.product_id = p.product_id
        WHERE 1=1
    """
    params = []

    if Enter_Product_id:
        query += " AND p.product_id = %s"
        params.append(Enter_Product_id)

    query += " GROUP BY p.product_id, p.product_name"

    if st.button("Search"):
        cursor.execute(query, tuple(params))
        Inventory_data = cursor.fetchall()

        if Inventory_data:
            df = pd.DataFrame(
                Inventory_data,
                columns=["Product id", "Product Name", "Total Production", "Total Sales", "Remaining Stock"]
            )
            st.dataframe(df)
        else:
            st.warning("No Match Record Found")

    # Show full inventory table
    st.header("Inventory Table")
    cursor.execute("""
        SELECT
            p.product_id,
            p.product_name,
            IFNULL(SUM(pr.quantity), 0) AS Total_Production,
            IFNULL(SUM(s.quantity), 0) AS Total_Sales,
            IFNULL(SUM(pr.quantity), 0) - IFNULL(SUM(s.quantity), 0) AS stock
        FROM products p
        LEFT JOIN production pr ON p.product_id = pr.product_id
        LEFT JOIN sales s ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
    """)
    Inventory_data = cursor.fetchall()

    if Inventory_data:
        df = pd.DataFrame(
            Inventory_data,
            columns=["Product id", "Product Name", "Total Production", "Total Sales", "Remaining Stock"]
        )
        st.dataframe(df)
    
        
   