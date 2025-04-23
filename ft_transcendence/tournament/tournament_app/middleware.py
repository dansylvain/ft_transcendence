from django.db import connection


class SchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the search path for the current request
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO tournament_schema")
        response = self.get_response(request)
        return response
