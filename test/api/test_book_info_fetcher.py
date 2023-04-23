import pytest
import requests

from app.api.book_info_fetcher import BookInfo, BookInfoFetcher
from app.errors.exceptions import BookNotFoundError, ExternalApiError


class TestBookInfoFercher():
    """
    Test class for BookInfoFetcher
    """

    def test_fetch_api_request_success(self, mocker):
        """
        Test for fetch method of BookInfoFetcher class
        Using mocker, mock the response of requests.get method
        and check if the response is correct
        """
        mock_obj = mocker.Mock()
        mock_obj.json.return_value = [
            {
                "summary": {
                    "title": "スタートライン : 一歩踏み出せば奇跡は起こる",
                    "author": "喜多川泰／著",
                    "isbn": "9784799311783",
                    "cover": "https://cover.openbd.jp/9784799311783.jpg"
                }
            }
        ]
        mocker.patch("app.api.book_info_fetcher.requests.get", return_value=mock_obj)
        book_info = BookInfoFetcher("9784799311783").fetch()
        assert book_info["summary"]["title"] == "スタートライン : 一歩踏み出せば奇跡は起こる"
        assert book_info["summary"]["author"] == "喜多川泰／著"
        assert book_info["summary"]["isbn"] == "9784799311783"
        assert book_info["summary"]["cover"] == "https://cover.openbd.jp/9784799311783.jpg"

    def test_fetch_api_request_timeout(self, mocker):
        """
        Test for fetch method of BookInfoFetcher class
        and catch the exception when timeout
        """
        mocker.patch("app.api.book_info_fetcher.requests.get", side_effect=requests.exceptions.Timeout)
        with pytest.raises(ExternalApiError):
            BookInfoFetcher("9784799311783").fetch()

    def test_fetch_api_request_http_error(self, mocker):
        """
        Test for fetch method of BookInfoFetcher class
        and catch the exception when http error
        """
        mocker.patch("app.api.book_info_fetcher.requests.get", side_effect=requests.exceptions.HTTPError)
        with pytest.raises(ExternalApiError):
            BookInfoFetcher("9784799311783").fetch()

    def test_get_book_info(self, mocker):
        """
        Test for get_book_info method of BookInfoFetcher class
        and check if the response is correct when the book is found
        """
        mock_obj = mocker.Mock()
        mock_obj.json.return_value = [
            {
                "summary": {
                    "title": "スタートライン : 一歩踏み出せば奇跡は起こる",
                    "author": "喜多川泰／著",
                    "isbn": " 9784799311783",
                    "cover": "https://cover.openbd.jp/9784799311783.jpg"
                }
            }
        ]
        mocker.patch("app.api.book_info_fetcher.requests.get", return_value=mock_obj)
        book_info = BookInfoFetcher("9784799311783").get_book_info()
        assert book_info.title == "スタートライン : 一歩踏み出せば奇跡は起こる"
        assert book_info.author == "喜多川泰／著"
        assert book_info.isbn == "9784799311783"
        assert book_info.cover == "https://cover.openbd.jp/9784799311783.jpg"

    def test_get_book_info_not_found(self, mocker):
        """
        Test for get_book_info method of BookInfoFetcher class
        and check if the response is correct when the book is not found
        """

        mocker.patch("app.api.book_info_fetcher.BookInfoFetcher.fetch", return_value=None)

        with pytest.raises(BookNotFoundError):
            BookInfoFetcher("97847741").get_book_info()


class TestBookInfo():
    """
    Test class for BookInfo
    """

    def test_book_info(self):
        """
        Test for BookInfo class
        """
        book_info = BookInfo(title="Pythonではじめる機械学習",
                             author="高橋 貴之",
                             isbn="9784798150402",
                             cover="https://cover.openbd.jp/9784798150402.jpg")
        assert book_info.title == "Pythonではじめる機械学習"
        assert book_info.author == "高橋 貴之"
        assert book_info.isbn == "9784798150402"
        assert book_info.cover == "https://cover.openbd.jp/9784798150402.jpg"

    def test_save_image_cover_path_exist(self, tmpdir):
        """
        Test for save_image method of BookInfo class
        when the cover path is exist
        """
        book_info = BookInfo(title="Pythonではじめる機械学習",
                             author="高橋 貴之",
                             isbn="9784798150402",
                             cover="https://cover.openbd.jp/9784798150402.jpg")
        save_result = book_info.save_image(str(tmpdir))
        assert save_result == f"{tmpdir}/9784798150402.jpg"
        assert len(tmpdir.listdir()) == 1
        assert tmpdir.listdir()[0].basename == "9784798150402.jpg"

    def test_save_image_cover_path_not_exist(self, tmpdir):
        """
        Test for save_image method of BookInfo class
        when the cover path is not exist
        """
        book_info = BookInfo(title="Pythonではじめる機械学習",
                             author="高橋 貴之",
                             isbn="9784798150402",
                             cover=None)
        save_result = book_info.save_image(str(tmpdir))
        assert save_result is None
        assert len(tmpdir.listdir()) == 0
