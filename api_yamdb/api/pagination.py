from rest_framework.pagination import PageNumberPagination


class CategoryGenrePagination(PageNumberPagination):
    page_size = 5
