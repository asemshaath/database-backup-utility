from .base import BackupStrategy
import psycopg2
from psycopg2 import sql
import subprocess
import os
import tempfile
import time
import getpass
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

class PostgresBackup(BackupStrategy):
    def backup(self, config):
        host = config.get("host")
        port = config.get("port")
        dbname = config.get("dbname")
        user = config.get("user")
        password = config.get("password")

        # Validate required fields
        if not all([host, port, dbname, user]):
            raise ValueError("Missing required database configuration (host, port, dbname, user)")

        # Prompt for password if not provided
        if not password:
            password = getpass.getpass(f"Enter password for PostgreSQL user '{user}': ")
        
        # Check version compatibility
        self._check_version_compatibility(host, port, user, password, dbname)

        # TEST CONNECTION FIRST (before creating any files)
        logger.debug("Testing database connection...")
        if not self.database_exists(dbname, user, password, host, port):
            raise ValueError(f"Cannot connect to database '{dbname}' - check credentials and database name")
        
        logger.debug("Connection successful")

        # NOW create temp file and backup
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        fd, the_temp_file = tempfile.mkstemp(suffix=".sql", prefix=f"{dbname}_{timestamp}_")
        os.close(fd)

        logger.debug(f"Backup file: {the_temp_file}")

        cmd = [
            "pg_dump",
            "-h", host,
            "-p", str(port),
            "-d", dbname,
            "-U", user,
            "-f", the_temp_file
        ]

        try:
            process = subprocess.Popen(
                cmd, 
                env=env, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            _, error = process.communicate()
            
            if process.returncode != 0:
                # Clean up on failure
                self._cleanup_temp_file(the_temp_file)                
                # This shouldn't happen if connection test passed, but handle it
                raise ValueError(f"pg_dump failed: {error.strip()}")
            
            logger.info(f"Backup created: {os.path.basename(the_temp_file)}")
            return the_temp_file
            
        except Exception as e:
            # Clean up temp file on any error
            if os.path.exists(the_temp_file):
                os.remove(the_temp_file)
            raise
    
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
                logger.info("The given database does not exist. Creating it...")
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
            logger.info(f"Database {dbname} restored successfully from {backup_file}")
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
            logger.error(f"Error connecting to PostgreSQL: {e}")
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
            logger.info(f"Database {db_name} created successfully.")
        except Exception as e:
            logger.info(f"Error creating database {db_name}: {e}")
    
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
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            # Parse specific errors
            if "password authentication failed" in error_msg:
                raise ValueError(f"Authentication failed - incorrect password for user '{user}'")
            elif "could not connect to server" in error_msg:
                raise ValueError(f"Could not connect to PostgreSQL at {host}:{port}")
            elif f'database "{dbname}" does not exist' in error_msg:
                raise ValueError(f"Database '{dbname}' does not exist")
            elif "role" in error_msg and "does not exist" in error_msg:
                raise ValueError(f"User '{user}' does not exist")
            else:
                raise ValueError(f"Connection failed: {error_msg}")

        except Exception as e:
            logger.info(f"Error connecting to PostgreSQL: {e}")
            return None 
    
    def _cleanup_temp_file(self, filepath):
        """Remove temporary file if it exists"""
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.debug(f"Cleaned up temp file: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {filepath}: {e}")

    def _check_version_compatibility(self, host, port, user, password, dbname):
        """Check if pg_dump version is compatible with database version"""
        
        # Get pg_dump version
        try:
            result = subprocess.run(
                ['pg_dump', '--version'],
                capture_output=True,
                text=True
            )
            dump_version_str = result.stdout.strip()
            dump_match = re.search(r'pg_dump \(PostgreSQL\) (\d+)', dump_version_str)
            if not dump_match:
                return  # Can't parse, let pg_dump handle it
            
            dump_version = int(dump_match.group(1))
        except Exception:
            return  # Can't check, let pg_dump handle it
        
        # Get database version
        try:
            conn = self.get_db_connection(dbname, user, password, host, port)
            cursor = conn.cursor()
            cursor.execute("SHOW server_version;")
            server_version_str = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            server_match = re.search(r'^(\d+)', server_version_str)
            if not server_match:
                return
            
            server_version = int(server_match.group(1))
        except Exception:
            return  # Can't check, let pg_dump handle it
        
        # Check compatibility
        if dump_version < server_version:
            raise ValueError(
                f"Version Mismatch Error\n\n"
                f"Your pg_dump (version {dump_version}) is too old for this database (version {server_version}).\n\n"
                f"To fix this:\n"
                f"  1. Upgrade PostgreSQL client tools to version {server_version}+\n"
                f"  2. See: https://github.com/asemshaath/afterchive#postgresql-version-requirements\n\n"
                f"Installation commands:\n"
                f"  Ubuntu/Debian: sudo apt install postgresql-client-{server_version}\n"
                f"  macOS: brew install postgresql@{server_version}\n"
                f"  RHEL/CentOS: sudo yum install postgresql{server_version}\n"
            )
