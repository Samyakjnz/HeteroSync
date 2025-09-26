# from pyhive import hive
# from System import System
# import os

# class Hive(System):
#     def __init__(self):
#         super().__init__("HIVE", "oplog.hiveql", "oplog_offsets")
#         self.conn = hive.Connection(host='localhost', port=10000, username='hive')
#         self.cursor = self.conn.cursor()
#         self.table = "student_course_grades"

#         # HDFS path where your CSV file should be placed
#         self.hdfs_csv_path = '/data/student_course_grades.csv'

#         create_main_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.table} (
#             student_id STRING,
#             course_id STRING,
#             roll_no STRING,
#             email_id STRING,
#             grade STRING,
#             last_update_ts INT
#         )
#         ROW FORMAT DELIMITED
#         FIELDS TERMINATED BY ','
#         STORED AS TEXTFILE
#         TBLPROPERTIES ("skip.header.line.count"="1")
#         """
#         self.cursor.execute(create_main_table)
#         os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/student_course_grades")
#         # Check if main table has data
#         self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
#         count = self.cursor.fetchall()[0][0]
#         if count == 0:
#             os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/project/student_course_grades.csv")
#             # LOAD from HDFS
#             print(f"Attempting to load data from HDFS path {self.hdfs_csv_path}...")
#             load_data_query = f"""
#             LOAD DATA LOCAL INPATH '{self.hdfs_csv_path}'
#             INTO TABLE {self.table}
#             """
#             self.cursor.execute(load_data_query)
#             print(f"Data loaded from {self.hdfs_csv_path} into Hive table {self.table}")

#             create_main_table = f"""
#             CREATE TABLE IF NOT EXISTS {self.table}_orc (
#                 student_id STRING,
#                 course_id STRING,
#                 roll_no STRING,
#                 email_id STRING,
#                 grade STRING,
#                 last_update_ts INT DEFAULT 0
#             )
#             STORED AS ORC
#             TBLPROPERTIES ("transactional"="true")
#             """
#             self.cursor.execute(create_main_table)
#             os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/student_course_grades_orc")
#             self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}_orc")
#             count = self.cursor.fetchall()[0][0]

#             if count == 0:
#                 load_into_orc = f"""
#                 INSERT INTO {self.table}_orc
#                 SELECT * FROM {self.table}
#                 """
#                 self.cursor.execute(load_into_orc)

#                 cleanup = f"""
#                 delete from {self.table}_orc where student_id = 'student-ID'
#                 """
#                 self.cursor.execute(cleanup)

#             # cleanup = f"""
#             # DROP TABLE {self.table}
#             # ALTER TABLE {self.table}_orc RENAME TO {self.table}
#             # """
#             #self.cursor.execute(cleanup)
#         else:
#             print(f"Table {self.table} already has data, skipping initial load.")
#         self.table = f"""{self.table}_orc"""
#         print(self.table)
            



#         create_offset_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.offset_table} (
#             system_name STRING,
#             byte_offset BIGINT
#         )
#         STORED AS ORC
#         TBLPROPERTIES ("transactional"="true")
#         """
#         self.cursor.execute(create_offset_table)
#         os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/oplog_offsets")
#         # Check if offset table needs initialization
#         self.cursor.execute(f"SELECT COUNT(*) FROM {self.offset_table}")
#         count = self.cursor.fetchall()[0][0]

#         if count == 0:
#             print("Initializing oplog_offsets table...")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('HIVE', 0)")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('MONGO', 0)")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('SQL', 0)")
#         else:
#             print("oplog_offsets table already initialized.")


#     def get(self, student_id, course_id, timestamp):
#         query = f"""
#         SELECT grade FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         grade = result[0][0] if result else "N/A"
#         self.log_operation(f"GET({student_id},{course_id})", timestamp)
#         return grade

#     def set(self, student_id, course_id, grade, timestamp):
#         update_query = f"""
#         UPDATE {self.table}
#         SET grade='{grade}', last_update_ts={timestamp}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(update_query)
#         self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)

#     def get_last_offset(self, system_name):
#         query = f"""
#         SELECT byte_offset FROM {self.offset_table}
#         WHERE system_name='{system_name}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else 0

#     def update_offset(self, system_name, new_offset):
#         update_query = f"update {self.offset_table} set byte_offset = {new_offset} where system_name = '{system_name}'"
#         #delete_query = f"DELETE FROM {self.offset_table} WHERE system_name='{system_name}'"
#         self.cursor.execute(update_query)
#         # insert_query = f"""
#         # INSERT INTO {self.offset_table} VALUES ('{system_name}', {new_offset})
#         # """
#         # self.cursor.execute(insert_query)

#     def get_current_timestamp_in_table(self, student_id, course_id):
#         query = f"""
#         SELECT last_update_ts FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None

#     def get_current_grade_in_table(self, student_id, course_id):
#         query = f"""
#         SELECT grade FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None


# from pyhive import hive
# from System import System
# import os
# import sys



# class Hive(System):
#     def __init__(self):
#         super().__init__("HIVE", "oplog.hiveql", "oplog_offsets")
#         # Define connection parameters
#         host = 'localhost'  # Assuming Hive is running on localhost
#         port = 10000  # Default port for HiveServer2
#         username = ''  # Replace with your Hive username (if applicable)
#         database = 'default'  # Replace with the desired database name
#         self.conn = hive.Connection(host=host, port=port, username=username, database=database)
#         self.cursor = self.conn.cursor()
#         self.table = "student_course_grades"


#         # HDFS path where your CSV file should be placed
#         self.hdfs_csv_path = '/data/student_course_grades.csv'

#         create_main_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.table} (
#             student_id STRING,
#             course_id STRING,
#             roll_no STRING,
#             email_id STRING,
#             grade STRING,
#             last_update_ts INT
#         )
#         ROW FORMAT DELIMITED
#         FIELDS TERMINATED BY ','
#         STORED AS TEXTFILE
#         """
#         self.cursor.execute(create_main_table)
#         #os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/student_course_grades")


#         # Check if main table has data
#         self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
#         count = self.cursor.fetchall()[0][0]
#         if count == 0:
#             #os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/project/student_course_grades.csv")
#             # LOAD from HDFS
#             print(f"Attempting to load data from HDFS path {self.hdfs_csv_path}...")
#             load_data_query = f"""
#             LOAD DATA LOCAL INPATH '{self.hdfs_csv_path}'
#             INTO TABLE {self.table}
#             """
#             self.cursor.execute(load_data_query)
#             print(f"Data loaded from {self.hdfs_csv_path} into Hive table {self.table}")

#             overwrite_query = f"""
#             INSERT OVERWRITE TABLE {self.table}
#             SELECT
#                 student_id,
#                 course_id,
#                 roll_no,
#                 email_id,
#                 grade,
#                 last_update_ts
#             FROM {self.table}
#             WHERE student_id != 'student-ID'
#             """
#             self.cursor.execute(overwrite_query)

#             # create_main_table_orc = f"""
#             # CREATE TABLE IF NOT EXISTS {self.table}_orc (
#             #     student_id STRING,
#             #     course_id STRING,
#             #     roll_no STRING,
#             #     email_id STRING,
#             #     grade STRING,
#             #     last_update_ts INT
#             # )
#             # STORED AS ORC
#             # """
#             # self.cursor.execute(create_main_table_orc)
#             # os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/student_course_grades_orc")
#             # self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}_orc")
#             # count = self.cursor.fetchall()[0][0]

#             # if count == 0:
#             #     load_into_orc = f"""
#             #     INSERT INTO {self.table}_orc
#             #     SELECT * FROM {self.table}
#             #     """
#             #     self.cursor.execute(load_into_orc)

#             #     cleanup = f"""
#             #     delete from {self.table}_orc where student_id = 'student-ID'
#             #     """
#             #     self.cursor.execute(cleanup)

#             # cleanup = f"""
#             # DROP TABLE {self.table}
#             # ALTER TABLE {self.table}_orc RENAME TO {self.table}
#             # """
#             #self.cursor.execute(cleanup)
#         else:
#             print(f"Table {self.table} already has data, skipping initial load.")
#         # self.table = f"""{self.table}_orc"""
#         # print(self.table)

#         # Create the offset table without transactional properties
#         create_offset_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.offset_table} (
#             system_name STRING,
#             byte_offset BIGINT
#         )
#         ROW FORMAT DELIMITED
#         FIELDS TERMINATED BY ','
#         STORED AS TEXTFILE
#         """
#         self.cursor.execute(create_offset_table)
#         #os.system("hdfs dfs -chmod -R 777 /user/hive/warehouse/oplog_offsets")
        
#         # Check if offset table needs initialization
#         self.cursor.execute(f"SELECT COUNT(*) FROM {self.offset_table}")
#         count = self.cursor.fetchall()[0][0]

#         if count == 0:
#             print("Initializing oplog_offsets table...")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('HIVE', 0)")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('MONGO', 0)")
#             self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('SQL', 0)")
#         else:
#             print("oplog_offsets table already initialized.")

#     def get(self, student_id, course_id, timestamp):
#         query = f"""
#         SELECT grade FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         grade = result[0][0] if result else "N/A"
#         self.log_operation(f"GET({student_id},{course_id})", timestamp)
#         return grade

#     def set(self, student_id, course_id, grade, timestamp):
#         # Instead of UPDATE, we'll simulate with an INSERT operation for non-transactional tables
#         insert_query = f"""
#         INSERT OVERWRITE TABLE {self.table}
#         SELECT 
#             CASE WHEN student_id='{student_id}' AND course_id='{course_id}' THEN '{grade}' ELSE grade END as grade,
#             student_id,
#             course_id,
#             roll_no,
#             email_id,
#             last_update_ts
#         FROM {self.table}
#         """
#         self.cursor.execute(insert_query)
#         self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)

#     def get_last_offset(self, system_name):
#         query = f"""
#         SELECT byte_offset FROM {self.offset_table}
#         WHERE system_name='{system_name}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else 0

#     def update_offset(self, system_name, new_offset):
#         overwrite_query = f"""
#         INSERT OVERWRITE TABLE {self.offset_table}
#         SELECT
#             CASE WHEN system_name = '{system_name}' THEN '{system_name}' ELSE system_name END AS system_name,
#             CASE WHEN system_name = '{system_name}' THEN {new_offset} ELSE byte_offset END AS byte_offset
#         FROM {self.offset_table}
#         """
#         self.cursor.execute(overwrite_query)


#     def get_current_timestamp_in_table(self, student_id, course_id):
#         query = f"""
#         SELECT last_update_ts FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None

#     def get_current_grade_in_table(self, student_id, course_id):
#         query = f"""
#         SELECT grade FROM {self.table}
#         WHERE student_id='{student_id}' AND course_id='{course_id}'
#         """
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None

# from pyhive import hive
# import sys
# import traceback
# from System import System

# class Hive(System):
#     def __init__(self):
#         super().__init__("HIVE", "oplog.hiveql", "oplog_offsets")

#         # HiveServer2 connection parameters
#         host = 'localhost'
#         port = 10000
#         username = ''        # Set your Hive username if needed
#         database = 'default' # Choose the Hive database

#         # 1) CONNECT
#         try:
#             print(f"[CONNECT] hive.Connection(host={host}, port={port}, database={database})")
#             self.conn = hive.Connection(host=host, port=port, username=username, database=database)
#             print("[OK] Connected to HiveServer2")
#         except Exception:
#             print("[ERROR] Failed to connect to HiveServer2:")
#             traceback.print_exc()
#             sys.exit(1)

#         self.cursor = self.conn.cursor()

#         # Table names and HDFS path
#         self.table = "student_course_grades"
#         self.hdfs_csv_path = '/data/student_course_grades.csv'

#         # 2) CREATE MAIN TABLE
#         create_main_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.table} (
#             student_id STRING,
#             course_id STRING,
#             roll_no STRING,
#             email_id STRING,
#             grade STRING,
#             last_update_ts INT
#         )
#         ROW FORMAT DELIMITED
#         FIELDS TERMINATED BY ','
#         STORED AS TEXTFILE
#         """
#         self._exec_print(create_main_table, "Create main table")

#         # 3) VERIFY MAIN TABLE EXISTS
#         self._list_tables("After CREATE TABLE")

#         # 4) INITIAL LOAD IF EMPTY
#         count = self._get_count(self.table)
#         if count == 0:
#             print(f"[LOAD] Table {self.table} is empty ({count} rows), loading data…")
#             load_sql = f"""
#             LOAD DATA LOCAL INPATH '{self.hdfs_csv_path}'
#             INTO TABLE {self.table}
#             """
#             self._exec_print(load_sql, "Load data into main table")
#         else:
#             print(f"[SKIP] Table {self.table} already has {count} rows, skipping load.")

#         # 5) CREATE OFFSET TABLE
#         create_offset_table = f"""
#         CREATE TABLE IF NOT EXISTS {self.offset_table} (
#             system_name STRING,
#             byte_offset BIGINT
#         )
#         ROW FORMAT DELIMITED
#         FIELDS TERMINATED BY ','
#         STORED AS TEXTFILE
#         """
#         self._exec_print(create_offset_table, "Create offset table")
#         self._list_tables("After OFFSET table creation")

#         # 6) INIT OFFSETS
#         offset_count = self._get_count(self.offset_table)
#         if offset_count == 0:
#             print("[INIT] Initializing oplog_offsets…")
#             for sys_name in ("HIVE", "MONGO", "SQL"):
#                 insert_sql = f"INSERT INTO {self.offset_table} VALUES ('{sys_name}', 0)"
#                 self._exec_print(insert_sql, f"Insert offset for {sys_name}")
#         else:
#             print(f"[SKIP] oplog_offsets already has {offset_count} rows")

#     def _exec_print(self, sql, label="SQL"):
#         print(f"[EXEC] {label}:\n{sql.strip()}")
#         try:
#             self.cursor.execute(sql)
#             print(f"[OK] {label} succeeded")
#         except Exception:
#             print(f"[ERROR] {label} failed:")
#             traceback.print_exc()

#     def _get_count(self, table):
#         try:
#             count_sql = f"SELECT COUNT(*) FROM {table}"
#             print(f"[QUERY] {count_sql}")
#             self.cursor.execute(count_sql)
#             cnt = self.cursor.fetchall()[0][0]
#             print(f"[RESULT] {table} has {cnt} rows")
#             return cnt
#         except Exception:
#             print(f"[ERROR] COUNT(*) on {table} failed:")
#             traceback.print_exc()
#             return -1

#     def _list_tables(self, context=""):
#         try:
#             show_sql = "SHOW TABLES"
#             print(f"[QUERY] {show_sql} ({context})")
#             self.cursor.execute(show_sql)
#             tables = [t[0] for t in self.cursor.fetchall()]
#             print(f"[TABLES] {tables}")
#         except Exception:
#             print(f"[ERROR] SHOW TABLES failed ({context}):")
#             traceback.print_exc()

#     def get(self, student_id, course_id, timestamp):
#         query = f"SELECT grade FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
#         self._exec_print(query, f"GET({student_id},{course_id})")
#         result = self.cursor.fetchall()
#         grade = result[0][0] if result else "N/A"
#         self.log_operation(f"GET({student_id},{course_id})", timestamp)
#         return grade

#     def set(self, student_id, course_id, grade, timestamp):
#         # Simulate UPDATE via INSERT OVERWRITE
#         insert_query = f"""
#         INSERT OVERWRITE TABLE {self.table}
#         SELECT
#             student_id,
#             course_id,
#             roll_no,
#             email_id,
#             CASE WHEN student_id='{student_id}' AND course_id='{course_id}' THEN '{grade}' ELSE grade END AS grade,
#             last_update_ts
#         FROM {self.table}
#         """
#         self._exec_print(insert_query, f"SET(({student_id},{course_id}),{grade})")
#         self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)

#     def get_last_offset(self, system_name):
#         query = f"SELECT byte_offset FROM {self.offset_table} WHERE system_name='{system_name}'"
#         self._exec_print(query, f"GET_OFFSET({system_name})")
#         result = self.cursor.fetchall()
#         return result[0][0] if result else 0

#     def update_offset(self, system_name, new_offset):
#         overwrite_query = f"""
#         INSERT OVERWRITE TABLE {self.offset_table}
#         SELECT
#             system_name,
#             CASE WHEN system_name='{system_name}' THEN {new_offset} ELSE byte_offset END AS byte_offset
#         FROM {self.offset_table}
#         """
#         self._exec_print(overwrite_query, f"UPDATE_OFFSET({system_name} -> {new_offset})")

#     def get_current_timestamp_in_table(self, student_id, course_id):
#         query = f"SELECT last_update_ts FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
#         self._exec_print(query, f"GET_TS({student_id},{course_id})")
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None

#     def get_current_grade_in_table(self, student_id, course_id):
#         query = f"SELECT grade FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
#         self._exec_print(query, f"GET_GRADE({student_id},{course_id})")
#         result = self.cursor.fetchall()
#         return result[0][0] if result else None

from pyhive import hive
import sys
import traceback
from System import System

class Hive(System):
    def __init__(self):
        super().__init__("HIVE", "oplog.hiveql", "oplog_offsets")

        # HiveServer2 connection parameters
        host = 'localhost'
        port = 10000
        username = ''        # Set your Hive username if needed
        database = 'default' # Choose the Hive database

        # 1) CONNECT
        try:
            self.conn = hive.Connection(host=host, port=port, username=username, database=database)
            print("[OK] Connected to HiveServer2")
        except Exception:
            print("[ERROR] Failed to connect to HiveServer2:")
            traceback.print_exc()
            sys.exit(1)

        self.cursor = self.conn.cursor()

        # Table names and HDFS path
        self.table = "student_course_grades"
        self.hdfs_csv_path = '/data/student_course_grades.csv'

        # 2) CREATE MAIN TABLE
        create_main_table = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            student_id STRING,
            course_id STRING,
            roll_no STRING,
            email_id STRING,
            grade STRING,
            last_update_ts INT
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ',' 
        STORED AS TEXTFILE
        """
        self._exec_sql(create_main_table)

        # 3) VERIFY MAIN TABLE EXISTS
        self._list_tables()

        # 4) INITIAL LOAD IF EMPTY
        count = self._get_count(self.table)
        if count == 0:
            print(f"[LOAD] Table {self.table} is empty ({count} rows), loading data…")
            load_sql = f"""
            LOAD DATA LOCAL INPATH '{self.hdfs_csv_path}'
            INTO TABLE {self.table}
            """
            self._exec_sql(load_sql)
            # Remove header row after loading
            cleanup_query = f"""
            INSERT OVERWRITE TABLE {self.table}
            SELECT *
            FROM {self.table}
            WHERE student_id != 'student-ID'
            """
            self._exec_sql(cleanup_query)

        else:
            print(f"[SKIP] Table {self.table} already has {count} rows, skipping load.")

        # 5) CREATE OFFSET TABLE
        create_offset_table = f"""
        CREATE TABLE IF NOT EXISTS {self.offset_table} (
            system_name STRING,
            byte_offset BIGINT
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ',' 
        STORED AS TEXTFILE
        """
        self._exec_sql(create_offset_table)
        self._list_tables()

        # 6) INIT OFFSETS
        offset_count = self._get_count(self.offset_table)
        if offset_count == 0:
            print("[INIT] Initializing oplog_offsets…")
            for sys_name in ("HIVE", "MONGO", "SQL"):
                insert_sql = f"INSERT INTO {self.offset_table} VALUES ('{sys_name}', 0)"
                self._exec_sql(insert_sql)
        else:
            print(f"[SKIP] oplog_offsets already has {offset_count} rows")

    def _exec_sql(self, sql):
        try:
            self.cursor.execute(sql)
            #print(f"[OK] SQL query executed successfully")
        except Exception:
            print(f"[ERROR] SQL query execution failed:")
            traceback.print_exc()

    def _get_count(self, table):
        try:
            count_sql = f"SELECT COUNT(*) FROM {table}"
            self.cursor.execute(count_sql)
            cnt = self.cursor.fetchall()[0][0]
            print(f"[RESULT] {table} has {cnt} rows")
            return cnt
        except Exception:
            print(f"[ERROR] COUNT(*) on {table} failed:")
            traceback.print_exc()
            return -1

    def _list_tables(self):
        try:
            show_sql = "SHOW TABLES"
            self.cursor.execute(show_sql)
            tables = [t[0] for t in self.cursor.fetchall()]
            print(f"[TABLES] {tables}")
        except Exception:
            print(f"[ERROR] SHOW TABLES failed:")
            traceback.print_exc()

    def get(self, student_id, course_id, timestamp):
        query = f"SELECT grade FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
        self._exec_sql(query)
        result = self.cursor.fetchall()
        grade = result[0][0] if result else "N/A"
        self.log_operation(f"GET({student_id},{course_id})", timestamp)
        return grade

    def set(self, student_id, course_id, grade, timestamp):
        # Simulate UPDATE via INSERT OVERWRITE
        insert_query = f"""
        INSERT OVERWRITE TABLE {self.table}
        SELECT
            student_id,
            course_id,
            roll_no,
            email_id,
            CASE WHEN student_id='{student_id}' AND course_id='{course_id}' THEN '{grade}' ELSE grade END AS grade,
            last_update_ts
        FROM {self.table}
        """
        self._exec_sql(insert_query)
        self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)

    def get_last_offset(self, system_name):
        query = f"SELECT byte_offset FROM {self.offset_table} WHERE system_name='{system_name}'"
        self._exec_sql(query)
        result = self.cursor.fetchall()
        return result[0][0] if result else 0

    def update_offset(self, system_name, new_offset):
        overwrite_query = f"""
        INSERT OVERWRITE TABLE {self.offset_table}
        SELECT
            system_name,
            CASE WHEN system_name='{system_name}' THEN {new_offset} ELSE byte_offset END AS byte_offset
        FROM {self.offset_table}
        """
        self._exec_sql(overwrite_query)

    def get_current_timestamp_in_table(self, student_id, course_id):
        query = f"SELECT last_update_ts FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
        self._exec_sql(query)
        result = self.cursor.fetchall()
        return result[0][0] if result else None

    def get_current_grade_in_table(self, student_id, course_id):
        query = f"SELECT grade FROM {self.table} WHERE student_id='{student_id}' AND course_id='{course_id}'"
        self._exec_sql(query)
        result = self.cursor.fetchall()
        return result[0][0] if result else None
