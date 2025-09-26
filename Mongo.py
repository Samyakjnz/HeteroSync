import pymongo
from System import System
import os
import csv

class Mongo(System):
    def __init__(self):
        super().__init__("MONGO", "oplog.mongoql", "oplog_offsets")
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["nosql"]
        self.collection = self.db["student_course_grades"]
        self.offset_collection = self.db[self.offset_table]

        # Initialize offset table if not already done
        if self.offset_collection.count_documents({}) == 0:
            print("Initializing oplog_offsets collection...")
            self.offset_collection.insert_many([
                {"system_name": "HIVE", "byte_offset": 0},
                {"system_name": "MONGO", "byte_offset": 0},
                {"system_name": "SQL", "byte_offset": 0}
            ])
        else:
            print("oplog_offsets collection already initialized.")

        if self.collection.count_documents({}) == 0:
            csv_path = '/home/shash/college/Third_Year/sem6/NoSQL/project/student_course_grades.csv'
            if os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    docs = []
                    for row in reader:
                        doc = {
                            "student_id": row['student-ID'],
                            "course_id": row['course-id'],
                            "roll_no": row['roll no'],
                            "email_id": row['email ID'],
                            "grade": row['grade'],
                            "last_update_ts": 0
                        }
                        docs.append(doc)
                    self.collection.insert_many(docs)
                print(f"Data loaded from {csv_path} into MongoDB collection {self.collection.name}")
            else:
                print(f"CSV file not found at {csv_path}. Skipping load.")

    def get(self, student_id, course_id, timestamp):
        result = self.collection.find_one({"student_id": student_id, "course_id": course_id})
        grade = result["grade"] if result else "N/A"
        self.log_operation(f"GET({student_id},{course_id})", timestamp)
        return grade

    def set(self, student_id, course_id, grade, timestamp):
        self.collection.update_one(
            {"student_id": student_id, "course_id": course_id},
            {"$set": {"grade": grade, "last_update_ts": timestamp}}
        )
        self.log_operation(f"SET(({student_id},{course_id}),{grade})", timestamp)

    def get_last_offset(self, system_name):
        result = self.offset_collection.find_one({"system_name": system_name})
        return result["byte_offset"] if result else 0

    def update_offset(self, system_name, new_offset):
        self.offset_collection.update_one(
            {"system_name": system_name},
            {"$set": {"byte_offset": new_offset}},
            upsert=True
        )

    def get_current_timestamp_in_table(self, student_id, course_id):
        result = self.collection.find_one({"student_id": student_id, "course_id": course_id})
        return result["last_update_ts"] if result else None

    def get_current_grade_in_table(self, student_id, course_id):
        result = self.collection.find_one({"student_id": student_id, "course_id": course_id})
        return result["grade"] if result else None
