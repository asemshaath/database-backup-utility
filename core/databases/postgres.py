from .base import BackupStrategy
import psycopg2
from psycopg2 import sql
import subprocess
import os
import tempfile
import time
import getpass

class PostgresBackup(BackupStrategy):
    def backup(self, config):
        # run pg_dump with right flags
        host = config.get("host", None)
        port = config.get("port", None)
        dbname = config.get("dbname", None)
        user = config.get("user", None)
        password = config.get("password", None)

        # Prompt for password if not provided
        if not password:
            password = getpass.getpass(f"Enter password for PostgreSQL user '{user}': ")

        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        fd, the_temp_file = tempfile.mkstemp(suffix=".sql", prefix=f"{dbname}_{timestamp}_")
        os.close(fd)

        print(f"Backup created: {the_temp_file}")

        if host and port and dbname and user:
            cmd = [
                "pg_dump",
                "-h", host,
                "-p", str(port),
                "-d", dbname,
                "-U", user,
                "-f", the_temp_file
            ]

            process = subprocess.Popen(cmd,env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, error = process.communicate()
            if process.returncode != 0:
                raise Exception(f"pg_dump failed: {error}")
            return the_temp_file
        else:
            raise ValueError("Missing required config parameters")
    
    def restore(self, config):
        backup_file = config.get("backup_file", None)
        host = config.get("host", None)
        port = config.get("port", None)
        dbname = config.get("dbname", None)
        user = config.get("user", None)
        password = config.get("password", None)
        if not backup_file or not os.path.exists(backup_file):
            raise ValueError("Backup file does not exist")
        
        # Prompt for password if not provided
        if not password:
            password = getpass.getpass(f"Enter password for PostgreSQL user '{user}': ")

        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        if host and port and dbname and user:
            if not self.database_exists(dbname, user, password, host, port):
                print("The given database does not exist. Creating it...")
                self.create_database(dbname, user, password, host, port)
            
            cmd = [
                "psql",
                "-h", host,
                "-p", str(port),
                "-d", dbname,
                "-U", user,
                "-f", backup_file
            ]
            process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, error = process.communicate()
            if process.returncode != 0:
                raise Exception(f"psql restore failed: {error}")
            print(f"Database {dbname} restored successfully from {backup_file}")
        else:
            raise ValueError("Missing required config parameters")

    def database_exists(self, db_name, user, password, host, port):
        """
        Checks if a PostgreSQL database with the given name exists.
        """
        try:
            # Connect to a default database (e.g., 'postgres') to query pg_database
            conn = self.get_db_connection("postgres", user, password, host, port)
            if conn is None:
                raise Exception("Failed to connect to PostgreSQL to check database existence")
            
            conn.autocommit = True
            cursor = conn.cursor()

            # Query pg_database to check for the existence of the specified database
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))

            exists = cursor.fetchone() is not None

            cursor.close()
            conn.close()
            return exists
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def create_database(self, db_name, user, password, host, port):
        """
        Creates a PostgreSQL database with the given name.
        """
        try:
            # Connect to a default database (e.g., 'postgres') to create a new database
            conn = self.get_db_connection("postgres", user, password, host, port)
            
            if conn is None:
                raise Exception("Failed to connect to PostgreSQL to create database")
            conn.autocommit = True
            cursor = conn.cursor()

            # Create the new database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            )

            cursor.close()
            conn.close()
            print(f"Database {db_name} created successfully.")
        except Exception as e:
            print(f"Error creating database {db_name}: {e}")
    
    def get_db_connection(self, dbname, user, password, host, port):
        try:

            conn = psycopg2.connect(
                database=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )            
            
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None 