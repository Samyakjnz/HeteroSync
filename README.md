# Heterogeneous Database Synchronization Framework

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.x-green.svg)](https://www.mongodb.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.x-blue.svg)](https://www.postgresql.org/)
[![Hive](https://img.shields.io/badge/Apache%20Hive-3.x-yellow.svg)](https://hive.apache.org/)

This project implements a robust data synchronization framework to maintain consistent student-course grade data across three heterogeneous database systems: **MongoDB**, **PostgreSQL**, and **Apache Hive**. The system supports independent `GET` and `SET` operations on each database and uses a sophisticated `MERGE` function to synchronize data using operation logs, without requiring direct access between databases.

## Core Concepts

The synchronization mechanism is built on three fundamental components:

### 1. Operation Logs (Oplogs)
Each database system (`MongoDB`, `SQL`, `Hive`) maintains its own append-only log file (e.g., `oplog.mongo`, `oplog.sql`). Every `GET` and `SET` operation performed on a system is recorded in its oplog with a timestamp, preserving the exact sequence of events. These logs are the sole source of information for the `MERGE` process.

**Example Oplog Entry:**
3, SET((SID1033, CSE016), B)

### 2. Offset Tables
To ensure merges are efficient and idempotent, each system maintains its own "offset table." This table tracks the last read position (in bytes) from every other system's oplog.

For example, if `HIVE`'s offset table shows `MONGO: 100`, it means Hive has already processed the first 100 bytes of `oplog.mongo`. The next time `HIVE.MERGE(MONGO)` is called, it will start reading `oplog.mongo` from byte 101, preventing the re-application of old operations.

### 3. The MERGE Function
The `MERGE` function is the core of the synchronization logic. When `SystemA.MERGE(SystemB)` is called:

1.  **Read Oplog:** System A reads System B's oplog (`oplog.B`) starting from the last known offset.
2.  **Filter Operations:** It only considers `SET` operations, as `GET` operations do not change state. It aggregates all updates, keeping only the most recent one for each unique key (student-ID, course-ID).
3.  **Conflict Resolution:** For each incoming update from System B, System A compares it with its own current record for that key. The update is applied if:
    -   The incoming timestamp is more recent than the current timestamp.
    -   The timestamps are identical, but the incoming grade is "better" (A > B > C).
4.  **Update Offset:** After the merge is complete, System A updates its offset table to reflect the new end-of-file position for `oplog.B`.

This approach guarantees key mathematical properties for reliable synchronization:
-   **Idempotency:** `A.MERGE(B)` can be repeated without changing the result.
-   **Commutativity:** The final state is the same regardless of merge order.
-   **Associativity:** `A.MERGE(B).MERGE(C)` is equivalent to `A.MERGE(B.MERGE(C))`.

## System Architecture

The project is implemented in Python with a modular, object-oriented design.

-   `main.py`: The entry point. It parses a test case file, interprets `GET`, `SET`, and `MERGE` commands, and delegates them to the appropriate system controller.
-   `system.py`: An abstract base class that defines the common interface for all database systems (`get`, `set`, `update_offset`, etc.). It contains the shared, generic `merge` logic.
-   `mongo.py`: The concrete implementation for MongoDB, handling connections and data operations using `pymongo`.
-   `postgres.py`: The concrete implementation for PostgreSQL, using `psycopg2` to execute `SELECT` and `UPDATE` queries.
-   `hive.py`: The concrete implementation for Apache Hive, using `pyhive` to connect to a Dockerized Hive instance and perform data operations.

## Installation and Setup

### Prerequisites
-   [Python](https://www.python.org/downloads/) 3.8+ and Pip.
-   [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose (for running Apache Hive).
-   A running local instance of [MongoDB](https://www.mongodb.com/try/download/community).
-   A running local instance of [PostgreSQL](https://www.postgresql.org/download/).

### Setup Instructions

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Set up the Python Environment**
    It is highly recommended to use a virtual environment.
    ```sh
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install required Python packages
    pip install -r requirements.txt
    ```

3.  **Set up Databases**
    -   **PostgreSQL & MongoDB**: Ensure your local servers are running and accessible. Create a database and user for the project if necessary.
    -   **Apache Hive**: The project is configured to use a Dockerized version of Hive. You may need to start it using a `docker-compose.yml` file (not included here, assumed to be part of the project setup).

4.  **Load Initial Data**
    Before running any operations, you must manually load the initial data from `student_course_grades.csv` into each of the three databases (MongoDB, PostgreSQL, and Hive). Ensure the schema includes a `last_update_ts` column, initialized to `0` or `NULL`.
