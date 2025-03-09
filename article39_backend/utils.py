from rest_framework.views import exception_handler
from django.shortcuts import render


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        # Extract all error messages into a plain string
        plain_errors = []
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    plain_errors.append(f"({field}) " + str(message))
            else:                
                plain_errors.append(f"({field}) " + str(messages))
        
        response.data = {
            "success": False,
            "message": "\n".join(plain_errors)
        }

    return response