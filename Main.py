from Mongo import Mongo
from Hive import Hive
from Postgres import Postgres

import re

def parse_command(cmd, systems):
    cmd = cmd.strip()
    if "MERGE" in cmd:
        sys1, rest = cmd.split('.')
        _, sys2 = rest.split('(')
        sys2 = sys2.strip(')')
        print(f"Executing {sys1}.MERGE({sys2})...")
        systems[sys1].merge(systems[sys2])
    else:
        timestamp_str, operation = cmd.split(",", 1)
        timestamp = int(timestamp_str.strip())
        print(f"Timestamp: {timestamp}")
        print(f"Operation: {operation}")
        operation = operation.strip()
        sys_name, action = operation.split(".", 1)
        print(f"System Name: {sys_name}")

        if action.startswith("SET"):
            inside = action[action.find("(")+1:action.rfind(")")]
            pair, grade = inside.split("),")
            sid, cid = pair.replace("(", "").split(",")
            sid, cid, grade = sid.strip(), cid.strip(), grade.strip()
            print(f"Executing {sys_name}.SET(({sid},{cid}), {grade})...")
            systems[sys_name].set(sid, cid, grade, timestamp)

        elif action.startswith("GET"):
            inside = action[action.find("(")+1:action.find(")")]
            sid, cid = inside.split(",")
            sid, cid = sid.strip(), cid.strip()
            result = systems[sys_name].get(sid, cid, timestamp)
            print(f"{sys_name}.GET({sid},{cid}) => {result}")

def main():
    systems = {
        "MONGO": Mongo(),
        "HIVE": Hive(),
        "SQL": Postgres()
    }

    testcase_file = "testcase.in"
    if not os.path.exists(testcase_file):
        print(f"Testcase file {testcase_file} not found.")
        return

    with open(testcase_file, "r") as f:
        for line in f:
            if line.strip():
                parse_command(line, systems)

if __name__ == "__main__":
    import os
    main()
