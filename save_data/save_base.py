from abc import ABC, abstractmethod


class SaveBase(ABC):
    """
    SaveBase abstract class.
    """

    def __init__(self, address: str):
        self.address = address

    @abstractmethod
    def save_info(self, path: str, data: dict):
        ...

    @abstractmethod
    def read_info(self, path: str):
        ...