from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    # Keep Swagger "Try it out" and default UI fetches tiny unless the caller
    # deliberately asks for more rows with page_size.
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100
