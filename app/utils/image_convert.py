import base64
import io
from typing import Union

from PIL import Image


class ImageBase64():

    @classmethod
    def encode(cls, image_path: str,
               no_image_path: Union[str, None] = "static/images/no_image.png") -> str:
        """encode is a function that encodes an image to base64.

        Parameters
        ----------
        image_path : str
            Path to the image

        no_image_path : str, optional
            Path to the no image image, by default "static/images/no_image.png"

        Returns
        -------
        str
            Base64 encoded image
        """
        try:
            with open(image_path, 'rb') as f:
                img = f.read()
        except FileNotFoundError:
            with open(no_image_path, 'rb') as f:
                img = f.read()
        return base64.b64encode(img)

    @classmethod
    def decode(cls, base64_img) -> Image:
        """decode is a function that decodes an image from base64.

        Parameters
        ----------
        base64_img : str
            Base64 encoded image

        Returns
        -------
        PIL.Image
            PIL.Image object
        """

        img = base64.b64decode(base64_img)
        return Image.open(io.BytesIO(img))
