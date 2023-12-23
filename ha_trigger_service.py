"""
    Script to trigger HA services

    By default this script looks for a config file in default location /etc/ha_config
    ha_config file should look like:

    url=http://homeassistant.local:8123
    token=12345678910abcdefghijklmnopqrstuvwxyz

    Usage:
    python3 ha_trigger_service.py --service scene.turn_on --entity scene.my_scene

    Specify config file location:
    python3 ha_trigger_service.py --config config_file_path --service media_player.turn_off --entity media_player.sonytv

"""

import sys
import argparse
import configparser
import requests

# pylint: disable=line-too-long


def main():
    """MAIN"""
    args = get_args()
    config = get_config(args.config)

    domain = args.service.split(".")[0]
    service_name = args.service.split(".")[1]
    trigger_service(
        url=config["url"],
        api_key=config["token"],
        domain=domain,
        service=service_name,
        entity_id=args.entity,
    )


def trigger_service(url, api_key, domain, service, entity_id):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    data = {"entity_id": entity_id}

    endpoint = f"{url}/api/services/{domain}/{service}"
    print(endpoint)
    response = requests.post(endpoint, json=data, headers=headers)

    if response.status_code == 200:
        print(
            f"Service '{domain}.{service}' triggered successfully for entity '{entity_id}'."
        )
    else:
        print(f"Failed to trigger service. Status code: {response.status_code}")


def get_config(path):
    """Get INI formatted config from path"""
    parser = configparser.ConfigParser()
    with open(path, encoding="utf8") as stream:
        parser.read_string("[default]\n" + stream.read())

    config = dict(parser["default"])

    if not config["url"]:
        sys.exit(f"No url found in config file {path}")

    if not config["token"]:
        sys.exit(f"No token found in config file {path}")

    return config


def get_args():
    """Get argparser args"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", help="Service to call", required=True)
    parser.add_argument("--entity", help="entity_id target", required=True)
    parser.add_argument(
        "--config",
        metavar="config_file_path",
        help="Path to config file",
        required=False,
        default="/etc/ha_config",
    )
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    if len(args.service.split(".")) < 2:
        sys.exit(
            "--service should be in the format of service_name.service_action i.e. media_player.turn_off"
        )

    return args


if __name__ == "__main__":
    main()
