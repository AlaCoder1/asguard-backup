from backend.ztna.utils import get_data_from_openziti


def get_identitie_from_ziti(id=None):
    """Get identities data from openziti API"""
    endpoint = "identities/"
    if id:
        endpoint = f"identities/{id}"
    return get_data_from_openziti(endpoint)


def get_enrollment_from_ziti(id=None):
    """Get enrollment data from openziti API"""
    endpoint = "enrollments/"
    if id:
        endpoint = f"enrollments/{id}"
    return get_data_from_openziti(endpoint)
