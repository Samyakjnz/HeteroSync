# # # import pymongo
# # # client = pymongo.MongoClient("mongodb://localhost:27017/")
# # # print(client.list_database_names())  # Should not throw error

# # import pymongo

# # def test_mongo_connection():
# #     try:
# #         # Connect to MongoDB server
# #         client = pymongo.MongoClient("mongodb://localhost:27017/")

# #         # Try to access the database
# #         db = client.test_database  # This is a temporary database for testing

# #         # Try to access a collection
# #         collection = db.test_collection

# #         # Insert a test document
# #         test_doc = {"name": "MongoDB Test", "status": "success"}
# #         collection.insert_one(test_doc)

# #         # Fetch the inserted document
# #         result = collection.find_one({"name": "MongoDB Test"})

# #         # Check if the document is found
# #         if result:
# #             print(f"Successfully connected to MongoDB! Document: {result}")
# #         else:
# #             print("Document not found.")
        
# #         # Cleanup: Remove the test document
# #         collection.delete_one({"name": "MongoDB Test"})
    
# #     except pymongo.errors.ConnectionError as e:
# #         print(f"Failed to connect to MongoDB: {e}")

# # # Run the test
# # test_mongo_connection()

# from pyhive import hive

# def test_pyhive_connection():
#     try:
#         conn = hive.Connection(host='localhost', port=10000, username='hive')
#         cursor = conn.cursor()
#         cursor.execute('SHOW DATABASES')
#         databases = cursor.fetchall()
#         print("Successfully connected to Hive!")
#         print("Databases:")
#         for db in databases:
#             print(db[0])
#         conn.close()
#     except Exception as e:
#         print(f"Failed to connect to Hive: {e}")

# if __name__ == "__main__":
#     test_pyhive_connection()

from pyhive import hive
import sys

# Define connection parameters
host = 'localhost'  # Assuming Hive is running on localhost
port = 10000  # Default port for HiveServer2
username = ''  # Replace with your Hive username (if applicable)
database = 'default'  # Replace with the desired database name

try:
    # Establish a connection to HiveServer2
    print(f"Attempting to connect to Hive on {host}:{port}...")
    conn = hive.Connection(host=host, port=port, username=username, database=database)
    
    # Check if connection is successful
    print(f"Connected to Hive server at {host}:{port} with database '{database}'.")

    # Execute a simple query to test the connection
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")  # You can replace this with another query

    # Fetch and print the result
    tables = cursor.fetchall()
    print("Tables in the current database:")
    for table in tables:
        print(table)

except Exception as e:
    print(f"Error while connecting to Hive: {e}", file=sys.stderr)
