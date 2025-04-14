import subprocess

POSTGRES_SERVICE_NAME = 'postgresql-x64-17'

def start_postgresql_service():
    try:
        subprocess.run(['net', 'start', POSTGRES_SERVICE_NAME], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting postgres: {e}")

def stop_postgresql_service():
    try:
        subprocess.run(['net', 'stop', POSTGRES_SERVICE_NAME], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping postgres: {e}")
