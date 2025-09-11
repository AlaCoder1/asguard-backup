from backend.ztna.models import Services
from backend.ztna.utils import get_data_from_openziti


def is_exist_config(service_name):
    """Check if the host or intercept config exist in database in HostConfigs or InterceptConfigs"""
    if len(Services.objects.filter(name=service_name)) == 0:
        return False
    return True


def get_service_from_ziti(id=None):
    """Get service data from openziti API"""
    endpoint = "services/"
    if id:
        endpoint = f"services/{id}"
    return get_data_from_openziti(endpoint)
