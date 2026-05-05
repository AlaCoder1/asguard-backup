import re


def is_valid_email(email):
    """Simple regex for validating an email"""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None