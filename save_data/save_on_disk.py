import json
import pathlib

from save_data.save_base import SaveBase


class SaveAddressBookOnDisk(SaveBase):

    def __init__(self, address: str):
        super().__init__(address)
        self.store_obj = pathlib.Path(address)
        if not self.store_obj.exists():
            with open(address, "w"):
                print(f"File '{address}' has been initialized.")

    def read_info(self, path: str) -> dict:
        """
        Method reads info from json file.
        :param path: Path to file.
        :return: Data from file as a dictionary.
        """
        with open(path, "r") as fh:
            try:
                file_data = json.load(fh)
            except ValueError:
                return {}
            return file_data

    def save_info(self, path: str, data: dict) -> None:
        """
        Method saves dictionary to json file.
        :param data: Dictionary that should be saved.
        :param path: Path to file in which the data should be saved.
        """
        with open(path, mode="w") as fh:
            json.dump(data, fh)
