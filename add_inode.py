"""
add_inodes.py

Usage:
  add_inodes.py -s <storage_address>  [-v <volume_name>] [-p <percent>]
  add_inodes.py (-h | --help)
  add_inodes.py --version

Options:
  -s <storage_address>    Address of the storage system.
  -v <volume_name>        Name of the specific volume to check [optional].
  -p <percent>            Percentage of inodes to add [optional, default: 15].
  -h --help               Show this help message.
  --version               Show version.

"""
import requests
import base64
import sys
import logging
from docopt import docopt
import warnings


# Suppress warnings
warnings.simplefilter("ignore")  # Ignores all warnings globally

# Global Constants
DEFAULT_PERCENT = 15  # 15% increase to the maximum inode
CRITICAL_PERCENT = 25

# Setup logging to file only
log_filename = 'add_inodes.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename)  # Log to file only
    ]
)

def Headers(username: str, password: str):
    """
    Returns the HTTP headers with Basic Authentication.
    """
    userpass = f"{username}:{password}"
    encoded_u = base64.b64encode(userpass.encode()).decode()
    return {"Authorization": f"Basic {encoded_u}"}

def myChoice(message: str) -> bool:
    """
    Prompt the user with a yes/no question and return True for 'yes', False for 'no'.
    """
    choice = input(message).strip().lower()
    if choice in ['yes', 'y']:
        return True
    return False

def get_inode_usage(storage_address: str, headers: dict, volume: str = None, percent=DEFAULT_PERCENT):
    """
    Fetches inode usage and updates the volume if the usage exceeds 90% of the maximum inodes.
    """
    url = f"https://{storage_address}/api/storage/volumes?fields=files"
    
    if volume:
        url += f"&name={volume}"

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        logging.debug(f"Response data: {data}")
        
        volumes = data.get('records', [])
        if not volumes:
            raise ValueError("Error: No volumes found.")
        
        for vol in volumes:
            volume_name = vol.get('name')
            uuid = vol.get('uuid')
            files = vol.get('files', {})
            maximum = files.get('maximum')
            used = files.get('used')

            if maximum == 0:
                print(f"Volume '{volume_name}' has 0 maximum inodes. Skipping update.")
                logging.warning(f"Volume '{volume_name}' has 0 maximum inodes. Skipping update.")
                continue

            if used >= 0.9 * maximum:
                print(f"Used inodes for volume '{volume_name}' are {used}, which is 90% or more of the maximum ({maximum}). Increasing maximum by {percent * 100}%.")
                logging.info(f"Used inodes for volume '{volume_name}' are {used}, which is 90% or more of the maximum ({maximum}). Increasing maximum by {percent * 100}%.")
                # Confirm before adding inodes if the percentage is above default
                print(percent)
                print(DEFAULT_PERCENT)
                print(CRITICAL_PERCENT)
                if percent*100 > DEFAULT_PERCENT and percent*100 <= CRITICAL_PERCENT:
                    choice_message = f"You are adding more than {DEFAULT_PERCENT}% of inodes. Are you sure? [yes/y/no/n] "
                    choice = myChoice(choice_message)
                    if not choice:
                        logmessage = "Exiting script"
                        print(logmessage)
                        logging.info(logmessage)
                        sys.exit(1)

                # You can't add more than CRITICAL_PERCENT inodes
                elif percent*100 > CRITICAL_PERCENT:
                    logmessage = f"You can't add more than {CRITICAL_PERCENT}% of inodes to any volume."
                    print(logmessage)    
                    logging.error(logmessage)
                    sys.exit(1)

                add_inodes(storage_address, headers, volume_name, uuid, maximum, percent)
            else:
                print(f"Used inodes for volume '{volume_name}': {used}. No update needed.")
                logging.info(f"Used inodes for volume '{volume_name}': {used}. No update needed.")

    except requests.RequestException as e:
        print(f"Error while fetching inode usage data: {e}")
        logging.error(f"Error while fetching inode usage data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")

def add_inodes(storage_address: str, headers: dict, volume_name: str, volume_uuid: str, maximum: int, percent: int):
    """
    Adds inodes to the specified volume.
    """
    url = f"https://{storage_address}/api/storage/volumes/{volume_uuid}"
    try:
        add_max = int(maximum * percent)
        new_maximum = int(maximum + add_max)

        payload = {
            "files": {
                "maximum": new_maximum
            }
        }

        # Send PATCH request to update maximum inodes
        patch_response = requests.patch(url, headers=headers, json=payload, verify=False)
        patch_response.raise_for_status()
        print(f"Successfully updated inodes for volume '{volume_name}'. New maximum: {new_maximum}")
        logging.info(f"Successfully updated inodes for volume '{volume_name}'. New maximum: {new_maximum}")
        logging.debug(f"Patch response: {patch_response.json()}")
    
    except requests.RequestException as e:
        print(f"Error while updating inodes for volume '{volume_name}': {e}")
        logging.error(f"Error while updating inodes for volume '{volume_name}': {e}")
    except Exception as e:
        print(f"An error occurred while updating inodes for volume '{volume_name}': {e}")
        logging.error(f"An error occurred while updating inodes for volume '{volume_name}': {e}")

if __name__ == "__main__":
    arguments = docopt(__doc__, version="add_inodes.py 1.0")

    # Extract arguments
    storage_address = arguments["-s"]
    volume_name = arguments["-v"]
    percent = int(arguments["-p"]) if arguments["-p"] else DEFAULT_PERCENT
    percent = percent / 100
    
    # Get username and password (use secure method in production)
    username = 'admin'
    password = 'netapp1234'

    # Set headers
    headers = Headers(username, password)

    # Perform operation
    try:
        get_inode_usage(storage_address, headers, volume_name, percent)
    except requests.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
