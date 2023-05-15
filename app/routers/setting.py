class AppRoutes:

    API_VERSION: str = "/v1.0"

    class Books:
        TAG: str = "books"
        PREFIX: str = "/books"
        POST_URL: str = "/"
        POST_OPENBD_URL: str = "/openbd"
        GET_URL: str = "/"

    class Authors:
        TAG: str = "authors"
        PREFIX: str = "/authors"
        GET_URL: str = "/"
