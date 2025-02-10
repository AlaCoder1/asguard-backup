from backend.ztna.utils import get_data


def get_service_from_ziti(id):
    """Get service data from openziti API"""
    endpoint = f"services/{id}"
    return get_data(endpoint)
