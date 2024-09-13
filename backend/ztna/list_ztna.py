from backend.ztna.utils import get_data


def get_identities(request):
    endpoint = "identities"
    return get_data(request, endpoint)


def get_routers(request):
    endpoint = "edge-routers"
    return get_data(request, endpoint)


def get_configs(request):
    endpoint = "configs"
    return get_data(request, endpoint)


def get_services(request):
    endpoint = "services"
    return get_data(request, endpoint)


def get_terminators(request):
    endpoint = "terminators"
    return get_data(request, endpoint)


def get_edge_router_policies(request):
    endpoint = "edge-router-policies"
    return get_data(request, endpoint)


def get_service_policies(request):
    endpoint = "service-policies"
    return get_data(request, endpoint)


def get_service_edge_router_policies(request):
    endpoint = "service-edge-router-policies"
    return get_data(request, endpoint)