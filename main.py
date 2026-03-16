import json
import os
import sys
import requests
from dotenv import load_dotenv


class Ipify:
    """A class for interacting with the Ipify service API to obtain an
        external IP address.
    """
    def get_ip(self):
        """It makes a request to the API and returns the current 
            external IP address.

        Args:
            None.

        Returns:
            str: the ip address as a string
        """
        response = requests.get('https://api.ipify.org/?format=json')
        return response.json()['ip']


class IpInfo:
    """A class for obtaining geographic data based on an IP address
        using the ipinfo.io service.
    """
    def get_geo_data(self, ip: str):
        """It makes a request to the API and returns the current 
            external IP address.

        Args:
            ip (str): The string with the ip address

        Returns:
            dict: Information about the provided ip address
        """
        response = requests.get('https://ipinfo.io/' + ip + '/geo')
        return response.json()


class YaDisk:
    """A class for managing files and folders on Yandex.Disk 
        using the REST API

    Args:
        token (str): The OAuth authorization token.
    """
    def __init__(self, token):
        self.token = 'OAuth ' + token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Authorization': self.token}

    def upload_file(self, file_name: str, overwrite: bool = False,
                    dir_name: str = 'ip_info'):
        """Uploads a local file to the specified folder on Yandex.Disk.

        Args:
            file_name (str): File name.
            overwrite (bool): Overwrite the file? True: YES, 
                False(by default): NO
            dir_name (str): Folder name. ('ip_info' by default)

        Returns:
            None.
        """

        response = requests.put(
            self.base_url, headers=self.headers, params={'path': dir_name})
        if response.status_code not in [201, 409]:
            date = response.json()
            print(f"{date.get('error')}: {date.get('message')}")
            sys.exit()

        response = requests.get(
            f"{self.base_url}/upload", headers=self.headers,
            params={'path': f"{dir_name}/{file_name}", 'overwrite': overwrite})
        if response.status_code != 200:
            date = response.json()
            print(f"{date.get('error')}: {date.get('message')}")
            sys.exit()

        upload_link = response.json()['href']
        with open(file_name, 'rb') as f:
            response = requests.put(upload_link, data=f)
            if response.status_code not in [201, 202]:
                date = response.json()
                print(f"{date.get('error')}: {date.get('message')}")
                sys.exit()


class FileManager:
    """A class for performing local file operations, such as saving and 
        deleting data.
    """
    def info_save(self, data: dict, file_name: str):
        """Saves the resulting dictionary to a file.

        Args:
            data (dict): Dictionary for saving.
            file_name (str): The name for the file being created.
        """
        if not data:
            return None

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def remove_file(self, file_name: str):
        """Deletes the file with the received name if it exists

        Args:
            file_name (str): The name of the file to delete.
        """
        try:
            os.remove(file_name)
        except FileNotFoundError:
            print(f"Warning: The file {file_name} was not found for deletion.")


if __name__ == '__main__':
    
    # Loading environment variables
    load_dotenv()

    # Initialization of services and parameters
    yd_token = os.getenv('YANDEX_TOKEN')
    dir_name = 'ip_info'
    file_name = 'data.json'

    ip_service = Ipify()
    geo_service = IpInfo()
    disk_service = YaDisk(yd_token)
    file_manager = FileManager()

    # Getting an IP address
    current_ip = ip_service.get_ip()
    
    # Getting geo-data and saving it to a local JSON file
    geo_data = geo_service.get_geo_data(current_ip)
    file_manager.info_save(geo_data, file_name)
    
    # Uploading a file to the cloud and cleaning temporary files
    try:
        disk_service.upload_file(file_name, True, dir_name)
    finally:
        file_manager.remove_file(file_name)
