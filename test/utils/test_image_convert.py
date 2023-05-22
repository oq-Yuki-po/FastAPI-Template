from PIL import Image

from app.utils.image_convert import ImageBase64


class TestImageBase64():

    def test_encode(self):
        """test_encode is a function to test encode function of ImageBase64 class.
        """

        encoded_image = ImageBase64.encode("app/static/images/no_image.png")

        assert encoded_image is not None
        assert isinstance(encoded_image, bytes)

    def test_encode_with_invalid_path(self):
        """test_encode_with_invalid_path is a function to test encode function of ImageBase64 class.
        """

        encoded_image = ImageBase64.encode("static/images/no_image_invalid.png", "app/static/images/no_image.png")

        assert encoded_image is not None
        assert isinstance(encoded_image, bytes)

    def test_decode(self):
        """test_decode is a function to test decode function of ImageBase64 class.
        """

        decoded_image = ImageBase64.decode(ImageBase64.encode("app/static/images/no_image.png"))

        assert decoded_image is not None
        assert isinstance(decoded_image, Image.Image)
