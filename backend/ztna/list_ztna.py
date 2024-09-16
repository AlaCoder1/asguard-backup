from backend.ztna.utils import get_data


def get_identities():
    endpoint = "identities"
    return get_data(endpoint)


def get_routers():
    endpoint = "routers"
    return get_data(endpoint)


def get_configs():
    endpoint = "configs"
    return get_data(endpoint)


def get_services():
    endpoint = "services"
    return get_data(endpoint)


def get_terminators():
    endpoint = "terminators"
    return get_data(endpoint)


def get_edge_router_policies():
    endpoint = "edge-router-policies"
    return get_data(endpoint)


def get_service_policies():
    endpoint = "service-policies"
    return get_data(endpoint)


def get_service_edge_router_policies():
    endpoint = "service-edge-router-policies"
    return get_data(endpoint)
