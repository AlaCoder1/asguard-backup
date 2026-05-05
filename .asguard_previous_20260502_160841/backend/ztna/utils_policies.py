from backend.ztna.utils import get_data_from_openziti


def get_router_policy_from_ziti(id=None):
    """Get edge router policy data from openziti API"""
    endpoint = "edge-routers-policies/"
    if id:
        endpoint = f"edge-routers-policies/{id}"
    return get_data_from_openziti(endpoint)


def get_service_policy_from_ziti(id=None):
    """Get service policy data from openziti API"""
    endpoint = "services-policies/"
    if id:
        endpoint = f"services-policies/{id}"
    return get_data_from_openziti(endpoint)


def get_services_router_policy_from_ziti(id=None):
    """Get service edge router policy data from openziti API"""
    endpoint = "services-edge-routers-policies/"
    if id:
        endpoint = f"services-edge-routers-policies/{id}"
    return get_data_from_openziti(endpoint)
