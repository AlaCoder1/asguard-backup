import json
import subprocess
import time

from django.core import serializers

from asguard.settings import ASGUARD_VERSION
from backend.dashboard.models import Services
from backend.dashboard.serializers import ServiceDataSerializer


DEFAULT_SERVICES = [
    "sshd",
    "suricata",
    "squid",
    "ipsec",
]


def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.strip()
    error = completed_process.stderr.strip()
    return output, error, completed_process.returncode


def _probe_service_state(service):
    status_install = True
    status_started = False
    status_enabled = False

    if service != "ipsec":
        enabled_output, enabled_error, enabled_code = run_command(f"sudo systemctl is-enabled {service}")
        active_output, active_error, active_code = run_command(f"sudo systemctl is-active {service}")

        status_enabled = enabled_code == 0 and enabled_output.strip() == "enabled"
        status_started = active_code == 0 and active_output.strip() == "active"
        status_install = not (
            "could not be found" in (enabled_error or "").lower()
            or "not-found" in (enabled_output or "").lower()
            or "could not be found" in (active_error or "").lower()
        )
    else:
        active_output, active_error, active_code = run_command("sudo ipsec status")
        status_started = active_code == 0 and active_output.strip() != ""
        status_enabled = status_started
        status_install = active_code == 0 or active_output.strip() != "" or active_error.strip() == ""

    return {
        "status_install": status_install,
        "status_started": status_started,
        "status_enabled": status_enabled,
    }


def service_action(service, status):
    if service != "ipsec":
        command = f"sudo systemctl {status} {service}"
    else:
        command = f"sudo ipsec {status}"

    output, error, returncode = run_command(command)
    if returncode != 0:
        return {
            "ok": False,
            "error": error or output or f"Command failed for {service}",
        }

    if status in {"start", "restart", "stop"}:
        time.sleep(1.2)

    state = _probe_service_state(service)

    if status in {"start", "restart"} and not state["status_started"]:
        return {
            "ok": False,
            "error": error or output or f"{service} is still stopped after {status}",
            "state": state,
        }

    if status == "stop" and state["status_started"]:
        return {
            "ok": False,
            "error": error or output or f"{service} is still running after stop",
            "state": state,
        }

    if status == "enable" and not state["status_enabled"]:
        return {
            "ok": False,
            "error": error or output or f"{service} is still disabled after enable",
            "state": state,
        }

    if status == "disable" and state["status_enabled"]:
        return {
            "ok": False,
            "error": error or output or f"{service} is still enabled after disable",
            "state": state,
        }

    return {
        "ok": True,
        "state": state,
        "output": output,
    }


def update_sevice_DB(service, data):
    payload = {
        "service_name": service,
        "description": data.get("description") or f"Service {service}",
        "status_enabled": bool(data.get("status_enabled")),
        "status_started": bool(data.get("status_started")),
        "status_install": bool(data.get("status_install", True)),
    }

    if Services.objects.filter(service_name=service).exists():
        object_config = Services.objects.get(service_name=service)
        service_serializer = ServiceDataSerializer(object_config, data=payload)
    else:
        service_serializer = ServiceDataSerializer(data=payload)

    if service_serializer.is_valid():
        service_serializer.save()
        return True
    return service_serializer.errors


def add_sevice_DB(data):
    return update_sevice_DB(data["service_name"], data)


def add_service_DB():
    list_info_services = []
    existing_services = list(
        Services.objects.exclude(service_name="strongswan").values_list("service_name", flat=True)
    )
    services_to_refresh = sorted(set(DEFAULT_SERVICES + existing_services))

    for service_name in services_to_refresh:
        state = _probe_service_state(service_name)
        service = {
            "service_name": service_name,
            "description": f"Service {service_name}",
            "status_enabled": state["status_enabled"],
            "status_started": state["status_started"],
            "status_install": state["status_install"],
        }
        list_info_services.append(json.dumps(service))
        update_sevice_DB(service_name, service)

    return list_info_services


def get_system_infomations():
    system_version, _, _ = run_command("sudo uname -a | cut -d ' ' -f 3")
    version_openssl, _, _ = run_command("sudo openssl version | cut -d' ' -f1-5 ")
    cpu_type, _, _ = run_command("sudo lscpu | grep \"Model name\" | cut -d':' -f2- | sed 's/^[[:space:]]*//'")
    cpu_type = " ".join(cpu_type.strip().splitlines())

    add_service_DB()
    info_object = Services.objects.all().exclude(service_name="strongswan")
    info_dict = serializers.serialize("json", info_object)
    res_rules = json.loads(info_dict)
    list_info_services = []
    for rule in res_rules:
        service = {
            "service_name": rule["fields"]["service_name"],
            "description": rule["fields"]["description"],
            "status_enabled": rule["fields"]["status_enabled"],
            "status_started": rule["fields"]["status_started"],
            "status_install": rule["fields"]["status_install"],
        }
        list_info_services.append(json.dumps(service))

    context = {
        "version_asguard": ASGUARD_VERSION.strip().strip("\n"),
        "system_version": system_version.strip().strip("\n"),
        "version_openssl": version_openssl.strip().strip("\n"),
        "cpu_type": cpu_type,
        "list_info_services": list_info_services,
    }
    return json.dumps(context)
