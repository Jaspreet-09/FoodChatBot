import mysql.connector

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Harman03',
    database='pandeyji_eatery',
)


def get_total_order_price(order_id):
    cursor=cnx.cursor()

    # Calling user defined function. It is a user defined function not stored procedure.
    query=f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    #Fetching the result
    result=cursor.fetchone()[0]

    #Closing the cursor
    cursor.close()

    return result

def insert_order_tracking(order_id,status):
    cursor=cnx.cursor()

    #Inserting the record into order tracking table
    insert_query="INSERT INTO order_tracking(order_id,status) VALUES (%s,%s)"

    cursor.execute(insert_query, (order_id,status))

    #comitting the changes
    cnx.commit()

    #closing the cursor
    cursor.close()


def insert_order_item(food_item,quantity,order_id):
    try:
        cursor=cnx.cursor()

        #calling the stored procedure in Mysql
        cursor.callproc('insert_order_item',(food_item,quantity,order_id))

        #committing the changes
        cnx.commit()

        #closing the cursor
        cursor.close()

        print('order item inserted successfully')

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        #Rollback changes if necessary
        cnx.rollback()

        return -1
    except Exception as e:
        print(f"An error occurred: {e}")

        #Rollback changes if necessary
        cnx.rollback()

        return -1




def get_next_order_id():
    cursor=cnx.cursor()

    #Executing the SQL query to get the next available order id.
    query="SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    #FETCHING the result
    result=cursor.fetchone()[0]

    #closing the cursor
    cursor.close()

    #Returning the next available order id
    if result is None:
        return 1
    else:
        return result+1


def get_order_status(order_id: int):
    try:

        # Create a cursor from the connection
        cursor = cnx.cursor()

        # Prepare the SQL query to retrieve the status based on order_id
        query = "SELECT status FROM order_tracking WHERE order_id = %s"

        # Execute the query with the order_id parameter
        cursor.execute(query, (order_id,))

        # Fetch the result
        status = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        #cnx.close()

        # Check if a status is found for the given order_id
        if status:
            return status[0]  # Return the first column value (status)
        else:
            return None  # Return None if no status found for the order_id

    except Exception as e:
        print(f"Error: {e}")
        return None

    else:
        cnx.close()

    return cnx
