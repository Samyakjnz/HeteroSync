import psycopg2
from System import System
import os
import csv

class Postgres(System):
    def __init__(self):
        super().__init__("SQL", "oplog.sql", "oplog_offsets")
        self.conn = psycopg2.connect(
            dbname="nosql_proj",
            user="postgres",
            password="db123",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()
        self.table = "student_course_grades"

        create_main_table = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            student_id TEXT,
            course_id TEXT,
            roll_no TEXT,
            email_id TEXT,
            grade TEXT,
            last_update_ts BIGINT DEFAULT 0
        )
        """
        self.cursor.execute(create_main_table)

        create_offset_table = f"""
        CREATE TABLE IF NOT EXISTS {self.offset_table} (
            system_name TEXT PRIMARY KEY,
            byte_offset BIGINT
        )
        """
        self.cursor.execute(create_offset_table)
        self.conn.commit()

        self.cursor.execute(f"SELECT COUNT(*) FROM {self.offset_table}")
        count = self.cursor.fetchone()[0]
        if count == 0:
            print("Initializing oplog_offsets table...")
            self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('HIVE', 0)")
            self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('MONGO', 0)")
            self.cursor.execute(f"INSERT INTO {self.offset_table} VALUES ('SQL', 0)")
            self.conn.commit()
        else:
            print("oplog_offsets table already initialized.")

        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table}")
        count = self.cursor.fetchone()[0]
        if count == 0:
            csv_path = '/home/shash/college/Third_Year/sem6/NoSQL/project/student_course_grades.csv'
            if os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)  # skip header
                    for row in reader:
                        self.cursor.execute(
                            f"INSERT INTO {self.table} (student_id, course_id, roll_no, email_id, grade) VALUES (%s, %s, %s, %s, %s)",
                            (row[0], row[1], row[2], row[3], row[4])
                        )
                self.conn.commit()
                print(f"Data loaded from {csv_path} into Postgres table {self.table}")
            else:
                print(f"CSV file not found at {csv_path}. Skipping load.")

    def get(self, student_id, course_id, timestamp):
        query = f"""
        SELECT grade FROM {self.table}
        WHERE student_id=%s AND course_id=%s
        """
        self.cursor.execute(query, (student_id, course_id))
        result = self.cursor.fetchone()
        grade = result[0] if result else "N/A"
        self.log_operation(f"GET({student_id},{course_id})", timestamp)
        self.conn.commit()
        return grade

    def set(self, student_id, course_id, grade, timestamp):
        update_query = f"""
        UPDATE {self.table}
        SET grade=%s, last_update_ts=%s
        WHERE student_id=%s AND course_id=%s
        """
        self.cursor.execute(update_query, (grade, timestamp, student_id, course_id))
        self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)
        self.conn.commit()

    def get_last_offset(self, system_name):
        query = f"SELECT byte_offset FROM {self.offset_table} WHERE system_name=%s"
        self.cursor.execute(query, (system_name,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_offset(self, system_name, new_offset):
        query = f"""
        INSERT INTO {self.offset_table} (system_name, byte_offset)
        VALUES (%s, %s)
        ON CONFLICT (system_name) DO UPDATE SET byte_offset = EXCLUDED.byte_offset
        """
        self.cursor.execute(query, (system_name, new_offset))
        self.conn.commit()

    def get_current_timestamp_in_table(self, student_id, course_id):
        query = f"SELECT last_update_ts FROM {self.table} WHERE student_id=%s AND course_id=%s"
        self.cursor.execute(query, (student_id, course_id))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_current_grade_in_table(self, student_id, course_id):
        query = f"SELECT grade FROM {self.table} WHERE student_id=%s AND course_id=%s"
        self.cursor.execute(query, (student_id, course_id))
        result = self.cursor.fetchone()
        return result[0] if result else None
