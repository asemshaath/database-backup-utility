from .base import BackupStrategy
# import psycopg2
import subprocess
import os
import tempfile
import time

class PostgresBackup(BackupStrategy):
    def backup(self, config):
        # run pg_dump with right flags
        host = config.get("host", None)
        port = config.get("port", None)
        dbname = config.get("dbname", None)
        user = config.get("user", None)
        password = config.get("password", None)

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
        # run pg_restore with right flags
        pass