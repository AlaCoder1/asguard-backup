from backend.ztna.utils import get_data


def get_identitie_from_ziti(id):
    """Get identity data from openziti API"""
    endpoint = f"identities/{id}"
    return get_data(endpoint)


def get_enrollment_from_ziti(id):
    """Get enrollment data from openziti API"""
    endpoint = f"enrollments/{id}"
    return get_data(endpoint)
