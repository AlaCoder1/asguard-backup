from backend.ztna.models import HostConfigs, InterceptConfigs
from backend.ztna.utils import get_data_from_openziti


def get_configuration_from_ziti(id=None):
    """Get configuration data from openziti API"""
    endpoint = "configs/"
    if id:
        endpoint = f"configs/{id}"
    return get_data_from_openziti(endpoint)


def get_payload_config_openziti(payload: dict):
    """Filter the payload to use it in openziti api by removing the unused fields:
            If the config is Host then remove Intercept fields
            If the config is Intercept then remove Host fields"""
    try:
        if payload["configTypeId"] == 'g7cIWbcGg':
                payload["data"].pop("address")
                payload["data"].pop("port")
                payload["data"].pop("protocol")
        else:
            payload["data"].pop("addresses")
            payload["data"].pop("portRanges")
            payload["data"].pop("protocols")
    except KeyError:
        pass
    # Remove description from payload
    payload.pop("Description")
    return payload


def get_payload_config_database(payload: dict):
    """Create a payload to save config on database"""
    payload_database={
        "name": payload["name"],
        "description": payload["Description"],
        }

    # Intercept Configuration
    if payload["configTypeId"] == 'g7cIWbcGg':
        payload_database['protocol'] = payload['data']['protocols'][0] # Fixed to access first protocol
        payload_database['address'] = payload['data']["addresses"][0] # Fixed to access first address
        payload_database['low'] = payload['data']["portRanges"][0]["low"]  # Fixed to access first low port range
        payload_database['high'] = payload['data']["portRanges"][0]["high"]  # Fixed to access first high port range

    # Host Configuration
    else :
        payload_database['protocol'] = payload['data']['protocol']
        payload_database['address'] = payload['data']["address"]
        payload_database['port'] = payload['data']["port"]
    return payload_database


def is_exist_config(config_name):
    """Check if the host or intercept config exist in database in HostConfigs or InterceptConfigs"""
    if len(HostConfigs.objects.filter(name=config_name)) == 0 or len(InterceptConfigs.objects.filter(name=config_name)) == 0:
        return False
    return True
