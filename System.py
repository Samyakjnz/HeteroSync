from abc import ABC, abstractmethod
import os

class System(ABC):
    def __init__(self, name, oplog_file, offset_table):
        self.name = name
        self.oplog_file = oplog_file
        self.offset_table = offset_table  

    def log_operation(self, operation, timestamp):
        with open(self.oplog_file, "a") as f:
            f.write(f"{timestamp}, {operation}\n")

    @abstractmethod
    def get_last_offset(self, system_name):
        pass
  
    @abstractmethod
    def update_offset(self, system_name, new_offset):
        pass

    @abstractmethod
    def get_current_timestamp_in_table(self, student_id, course_id):
        pass

    @abstractmethod
    def get_current_grade_in_table(self, student_id, course_id):
        pass

    @abstractmethod
    def get(self, student_id, course_id, timestamp):
        pass

    @abstractmethod
    def set(self, student_id, course_id, grade, timestamp):
        pass

    def merge(self, other_system):
        latest_updates = {}
        last_offset = other_system.get_last_offset(other_system.name)

        with open(other_system.oplog_file, "r") as f:
            f.seek(last_offset)
            while True:
                line = f.readline()
                if not line:
                    break

                parts = line.strip().split(",", 1)
                if len(parts) != 2 or "SET" not in parts[1]:
                    continue
                timestamp = int(parts[0].strip())
                operation = parts[1].strip()
                pair, grade = operation.split("),")[0][4:], operation.split("),")[1]
                sid, cid = pair.replace("(", "").split(",")
                key = (sid.strip(), cid.strip())
                grade = grade.strip()
                grade = grade.replace(")", "").strip()
                if key not in latest_updates:
                    latest_updates[key] = (timestamp, grade)
                else:
                    prev_timestamp, prev_grade = latest_updates[key]
                    if timestamp > prev_timestamp or (timestamp == prev_timestamp and grade < prev_grade):
                        latest_updates[key] = (timestamp, grade)

        # Step 2: Compare and update system data
        for (sid, cid), (incoming_timestamp, incoming_grade) in latest_updates.items():
            current_timestamp = self.get_current_timestamp_in_table(sid, cid)
            current_grade = self.get_current_grade_in_table(sid, cid)

            should_update = False
            if current_timestamp is None or current_timestamp == 0:
                should_update = True
            elif incoming_timestamp > current_timestamp:
                should_update = True
            elif incoming_timestamp == current_timestamp and incoming_grade < current_grade:
                should_update = True
            if should_update:
                self.set(sid, cid, incoming_grade, incoming_timestamp)

        # Step 3: Update the new last read offset
        new_offset = os.path.getsize(other_system.oplog_file)
        self.update_offset(other_system.name, new_offset)
