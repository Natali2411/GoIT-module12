from __future__ import annotations

import json
import re
from collections import UserDict
from datetime import datetime
from re import Match
from typing import Tuple, Any, Generator

from save_data.save_base import SaveBase

DATE_FORMAT = "%d-%m-%Y"


class RecordAlreadyExistsException(Exception):
    """
    Custom exception class for catching exceptions in case of the try to add a record
    that already exists in the AddressBook.
    """
    pass


class Field:
    """
    Base class that describes the logic for all types of fields.
    """

    def __init__(self, value: Any):
        self.__value = value

    def __str__(self):
        return str(self.__value)


class Name(Field):
    """
    This class is a derived class from Field and needed for storing name of the client.
    """

    def __init__(self, client_name: str):
        self.value = client_name
        super().__init__(value=self.value)

    @property
    def value(self) -> str:
        """
        Getter for getting Name field value.
        :return: Name value.
        """
        return self.__value

    @value.setter
    def value(self, client_name: str) -> None:
        """
        Setter for setting Name value.
        :param client_name: Client name string.
        :return: None.
        """
        self.__value = client_name


class Birthday(Field):
    """
    This class is a derived class from Field and needed for storing birthday of the
    client.
    """

    def __init__(self, birthday: str = None):
        self.value = birthday
        super().__init__(value=self.value)

    @property
    def value(self) -> datetime.date:
        """
        Getter method to return birthday value.
        :return: Birthday value.
        """
        return self.__value

    @value.setter
    def value(self, birthday: str) -> None:
        """
        Setter for birthday value.
        :param birthday: Birthday value.
        :return: None.
        """
        if birthday is None:
            self.__value = birthday
            return
        try:
            birthday_dt: datetime.date = datetime.strptime(birthday,
                                                           DATE_FORMAT).date()
            self.__value = birthday_dt
        except Exception:
            raise ValueError(f"Client birthday '{birthday}' or date format is "
                             f"incorrect. Expected date format is '{DATE_FORMAT}'."
                             f"Check it, please.")


class Phone(Field):
    """
    This class is a derived class from Field and needed for storing phone of the client.
    """

    def __init__(self, phone: str):
        self.value = phone
        super().__init__(value=self.value)

    @property
    def value(self) -> str:
        """
        Getter method for getting phone number value.
        :return: Phone value.
        """
        return self.__value

    @value.setter
    def value(self, phone: str):
        match: Match[bytes] | None = re.search('\d+', phone)
        numbers = match.group() if match else ""
        phone_number_len: int = len(phone)
        if phone_number_len != 10 or len(numbers) != phone_number_len:
            raise ValueError(f"Phone number must have only digits with length "
                             f"10, but number: '{phone}' was given with the "
                             f"length {phone_number_len}")
        self.__value = phone


class Record:
    """
    This class describes the logic of storing data about the client and all his/her
    phones.
    """

    def __init__(self, name: str, birthday: str = None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones:" \
               f" {'; '.join(p.value for p in self.phones)}"

    def __repr__(self) -> str:
        birthday: datetime = self.birthday.value
        birthday_str = None
        if birthday:
            birthday_str = birthday.strftime(DATE_FORMAT)
        return json.dumps(
            {
                self.name.value:
                    {
                        "phones": [phone_num.value for phone_num in self.phones],
                        "birthday": birthday_str
                    }
            }
        )

    def days_to_birthday(self) -> int:
        """
        Method calculates the number of days to the next client's birthday. The method
        returns the number of days without fractional part.
        :return: Number of days.
        """
        if self.birthday.value:
            today = datetime.today()
            today_day, today_month, today_year = today.day, today.month, today.year
            birth_day, birth_month = self.birthday.value.day, self.birthday.value.month
            next_birthday_year = today_year

            if today_month > birth_month or (today_month == birth_month and today_day
                                             > birth_day):
                next_birthday_year = today_year + 1
            time_diff = datetime(next_birthday_year, birth_month, birth_day) - today
            days_to_next_birthday = time_diff.days
            return days_to_next_birthday
        else:
            raise ValueError("There is no information about the client birthday. Add "
                             "it first and call this method again.")

    def get_phone_by_number(self, phone_num: str) -> Tuple[Any, int] | Tuple[None, None]:
        """
        Method iterates through the list of phone objects and returns the object that
        has 'phone_num' as a phone value.
        :param phone_num: Phone number string.
        :return: Phone object and it's index in the list.
        """
        for idx, phone in enumerate(self.phones):
            if phone.value == phone_num:
                return phone, idx
        return None, None

    def add_phone(self, phone_num: str) -> str:
        """
        Method adds Phone instances into the list of phones for a particular client.
        :param phone_num: Phone number as a string.
        :return: Notification with the information about adding phone.
        """
        self.phones.append(Phone(phone=phone_num))
        return f"Phone number '{phone_num}' was successfully added to the contact '" \
               f"{self.name.value}'"

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """
        Method founds the phone number in a list of other client's numbers and edits
        it if the number was found.
        :param old_phone: The phone that must be changed.
        :param new_phone: The new phone number.
        :return: None.
        """
        found_phone, idx = self.get_phone_by_number(phone_num=old_phone)
        if found_phone:
            self.phones[idx].value = new_phone
        else:
            raise ValueError(
                f"Phone with the number '{old_phone}' was not found for the "
                f"user '{self.name.value}'")

    def remove_phone(self, phone_num: str) -> None:
        """
        Method that removes phone number from the list of client's numbers.
        :param phone_num: Phone number that should be removed.
        :return: None.
        """
        _, idx = self.get_phone_by_number(phone_num=phone_num)
        self.phones.pop(idx)

    def find_phone(self, phone_num: str) -> Phone:
        """
        Method that searches for a phone number and returns a Phone object if the
        number was found.
        :param phone_num: Phone number that should be found.
        :return: The Phone object of found phone number or None.
        """
        found_phone, _ = self.get_phone_by_number(phone_num=phone_num)
        return found_phone

    def add_birthday(self, birthday: str) -> str:
        """
        Method adds Birthday instance to the field 'birthday' for the particular client.
        :param birthday: Phone number as a string.
        :return: Notification with the information about adding birthday.
        """
        self.birthday = Birthday(birthday=birthday)
        return f"Birthday '{birthday}' was successfully added to the birthday '" \
               f"{self.name.value}'"


class AddressBook(UserDict):
    """
    Class that describes the logic of saving client's records in the address book and
    making manipulations with the records.
    """

    def __init__(self, data_save_tool: SaveBase):
        super().__init__()
        self.data_save_tool = data_save_tool
        self.data.update(self.data_save_tool.read_info(path=self.data_save_tool.address))

    def iterator(self, record_num: int = None) -> Generator:
        """
        Method that implements the logic of the generator to retrieve records from the
        Address Book by chunks.
        :param record_num: The size of chunks of the records from the Address Book.
        :return: Generator.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        book_items = list(address_book.items())
        if not record_num:
            step = 1
        else:
            step = record_num
        for i in range(0, len(book_items), step):
            start = i
            stop = i + step
            yield book_items[start:stop]

    def add_record(self, record: Record) -> None:
        """
        Method adds Record objects into the address book using client name as a key
        and the object as a value.
        :param record: Record instance that has an information about client name and
        her/his phone numbers.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        if record.name.value not in address_book:
            self.data[record.name.value] = record
            record_data = repr(record)
            address_book.update(json.loads(record_data))
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise RecordAlreadyExistsException(f"Record with the name '"
                                               f"{record.name.value}' already exists "
                                               f"in the address book dictionary")

    def update_record(self, record: Record) -> None:
        """
        Method makes record update in the data saving tool.
        :param record: Updated Record instance.
        :return: None.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        found_record = address_book.get(record.name.value)
        if found_record:
            address_book[record.name.value] = json.loads(repr(record))[record.name.value]
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise ValueError(f"The contact with the name '{record.name.value}' has not"
                             f" been found in the Address Book")

    def find(self, name: str) -> Record:
        """
        Method finds records from the address book by client's name.
        :param name: The name of a client.
        :return: Record from the address book for specific client.
        """
        record: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address).get(name)
        if record:
            record_obj = Record(name=name, birthday=record.get("birthday"))
            for phone in record["phones"]:
                record_obj.add_phone(phone_num=phone)
            return record_obj
        else:
            return None

    def search_contact(self, search_phrase: str) -> Generator:
        """
        Method searches info about contact by name or phone using approximate equality.
        :param search_phrase: The phrase which is used for the searching contacts in the
        Address Book.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        for contact_name, contact_info in address_book.items():
            found_phones = list(filter(lambda phone: search_phrase in phone,
                                       contact_info["phones"]))
            if any([search_phrase.lower() in contact_name.lower(), found_phones]):
                yield {"name": contact_name, "info": contact_info}

    def delete(self, name: str) -> None:
        """
        Method deletes the record from the address book for the specific client by
        his/her name.
        :param name: Client's name.
        :return: None.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        record: dict = address_book.get(name)
        if record:
            self.data.pop(name)
            address_book.pop(name)
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise ValueError(f"Contact with the name '{name}' doesn't exist in the "
                             f"Address Book")
