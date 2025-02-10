from backend.ztna.utils import get_data


def get_router_policy_from_ziti(id):
    """Get edge router policy data from openziti API"""
    endpoint = f"edge-routers-policies/{id}"
    return get_data(endpoint)


def get_service_policy_from_ziti(id):
    """Get service policy data from openziti API"""
    endpoint = f"services-policies/{id}"
    return get_data(endpoint)


def get_router_policy_from_ziti(id):
    """Get service edge router policy data from openziti API"""
    endpoint = f"services-edge-routers-policies/{id}"
    return get_data(endpoint)
