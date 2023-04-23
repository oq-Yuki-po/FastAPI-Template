from dataclasses import dataclass
from typing import Optional

import requests

from app import app_logger
from app.errors.exceptions import BookNotFoundError, ExternalApiError


@dataclass
class BookInfo():
    """
    Class for BookInfo

    Parameters
    ----------
    title : str
        title of the book
    author : str
        author of the book
    isbn : str
        isbn of the book
    cover : str
        cover image url of the book
    """
    title: str
    author: str
    isbn: str
    cover: str

    def save_image(self, directory_path: str) -> Optional[str]:
        """
        Save cover image of the book

        Parameters
        ----------
        directory_path : str
            directory path to save cover image

        Returns
        -------
        Optional[str]
            path of the cover image
            when cover image is not found, return None
        """
        if self.cover is None:
            return None
        else:
            res = requests.get(self.cover, timeout=10)
            res.raise_for_status()
            with open(f"{directory_path}/{self.isbn}.jpg", "wb") as f:
                f.write(res.content)
            return f"{directory_path}/{self.isbn}.jpg"


class BookInfoFetcher:
    """
    Class for fetching book information from openbd API

    Parameters
    ----------
    isbn : str
        isbn of the book
    """

    def __init__(self, isbn):
        self.isbn = isbn

    def fetch(self):
        """
        Fetch book information from openbd API

        Returns
        -------
        dict
            book information

        Raises
        ------
        ExternalApiError
            when timeout or http error
        """
        url = "https://api.openbd.jp/v1/get"
        params = {"isbn": self.isbn}
        try:
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
        except (requests.exceptions.Timeout, requests.exceptions.HTTPError) as error:
            app_logger.error("openbd Error: %s", error)
            raise ExternalApiError from error
        return res.json()[0]

    def get_book_info(self) -> Optional[BookInfo]:
        """
        Get book information from openbd API

        Returns
        -------
        BookInfo
            book information

        Raises
        ------
        BookNotFoundError
            when the book is not found
        """

        if (book_info := self.fetch()) is None:
            app_logger.error("Book not found: %s", self.isbn)
            raise BookNotFoundError
        else:
            return BookInfo(title=book_info["summary"]["title"],
                            author=book_info["summary"]["author"],
                            isbn=self.isbn,
                            cover=book_info["summary"].get("cover"))
