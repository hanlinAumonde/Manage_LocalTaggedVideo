import subprocess
import time
import tkinter
import pymongo

DOCKER_CONTAINER_NAME = "mongodb-test"
DOCKER_LOCAL_VOLUME_PATH = "your_local_volume_path"  # Replace with your local volume path

# def setup_mongodb():
#     """Check and setup MongoDB connection"""
#     try:
#         # Try to connect to MongoDB
#         client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
#         # Force a command to check the connection
#         client.admin.command('ping')
#         print("MongoDB connection successful.")
#         return True
#     except pymongo.errors.ServerSelectionTimeoutError:
#         print("Error: Could not connect to MongoDB server.")
#         print("Please make sure MongoDB is installed and running on localhost:27017.")
#         return False
#     except Exception as e:
#         print(f"MongoDB error: {str(e)}")
#         return False

def setup_mongodb():
    """Try connecting to MongoDB; if unavailable, create/start a Docker container."""
    def try_connect():
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            print("MongoDB connection successful.")
            return True
        except:
            return False

    def container_exists(name):
        try:
            output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Names}}"]).decode()
            return name in output
        except:
            return False

    def container_running(name):
        try:
            output = subprocess.check_output(
                ["docker", "ps", "--filter", f"name={name}", "--filter", "status=running", "--format", "{{.Names}}"]
            ).decode()
            return name in output
        except:
            return False

    def start_container(name):
        try:
            subprocess.check_call(["docker", "start", name])
            print(f"Started existing MongoDB container '{name}'.")
            CONTAINER_STARTED_BY_THIS_SCRIPT = True
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start container: {e}")
            return False

    def create_container(name):
        try:
            print(f"Creating new MongoDB container '{name}'...")
            subprocess.check_call([
                "docker", "run", "-d",
                "--name", name,
                "-p", "27017:27017",
                "-v", f"{DOCKER_LOCAL_VOLUME_PATH}:/data/db",
                "mongo:latest"
            ])
            print(f"MongoDB container '{name}' created and started.")
            CONTAINER_STARTED_BY_THIS_SCRIPT = True
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create MongoDB container: {e}")
            return False

    def wait_for_container():
        print("Waiting for MongoDB container to initialize...")
        for _ in range(5):
            time.sleep(2)
            print("Retrying connection...")
            if try_connect():
                return True
        print("Failed to connect to MongoDB after 5 attempts.")
        return False

    # Step 1: Try initial connection
    if try_connect():
        return True, False
    
    print("MongoDB not running on localhost:27017, attempting to resolve with Docker...")

    # Step 2: Check Docker
    # Step 3: Wait and retry (up to 5 times, if still not connected, return False)
    if container_exists(DOCKER_CONTAINER_NAME):
        if not container_running(DOCKER_CONTAINER_NAME):
            if start_container(DOCKER_CONTAINER_NAME):
                return wait_for_container(), True
            return False, False
    else:
        if create_container(DOCKER_CONTAINER_NAME):
            return wait_for_container(), True

    print("Failed to create or start MongoDB container.")
    return False, False

def on_close(root:tkinter.Tk, started_by_app:bool):
    if started_by_app:
        #close the Docker container in another thread
        stop_container_async(DOCKER_CONTAINER_NAME)
    root.destroy()

def stop_container_async(name):
    def worker():
        try:
            subprocess.check_call(["docker", "stop", name])
            print(f"MongoDB container '{name}' stopped.")
        except Exception as e:
            print(f"Error stopping container: {e}")
    import threading
    threading.Thread(target=worker, daemon=True).start()