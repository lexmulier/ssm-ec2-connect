import json
import os
import sys
from os import path
from typing import Optional

import boto3
from simple_term_menu import TerminalMenu

DEFAULT_PROFILE: str = "default"

# List regions to include
REGIONS: list[str] = [
    "EU - eu-west-1",
    "US - us-east-1",
    "AP - ap-northeast-1",
    "SA - sa-east-1",
]

# Filter instance types by name
INSTANCE_TYPES: list[str] = [
    "Process",
    "Web",
    "Database",
    "FTP",
]


def config_util(file_path: str) -> dict | None:
    if path.isfile(file_path):
        config_file = open(file_path)
        return json.load(config_file)
    return None


def menu_picker_util(options: list, title: str) -> str:
    menu_options = (
        options
        if not isinstance(options[0], (list, tuple))
        else [x[0] for x in options]
    )
    menu = TerminalMenu(menu_options, title=f"{title}\n{20*'='}")
    option_index = menu.show()
    return options[option_index]


class SSMConnect:
    _aws_region: str
    _profile: str

    def __init__(self, config: Optional[dict] = None):
        self._config = config
        self._set_account_and_profile()

    def _set_account_and_profile(self) -> None:
        if not self._config:
            self._profile = DEFAULT_PROFILE
        elif len(self._config) <= 1:
            self._profile = self._config[0]["profile_name"]
        else:
            chosen_account = menu_picker_util(
                [tuple(d.values()) for d in self._config], title="Pick AWS Account..."
            )
            self._profile = chosen_account[1]

    def _get_boto3_ec2_resource(self) -> boto3.resource:
        boto3_session = boto3.session.Session(
            profile_name=self._profile, region_name=self._aws_region
        )
        return boto3_session.resource("ec2")

    def _get_instances(self, chosen_type: str) -> list[tuple[str, str]]:
        ec2 = self._get_boto3_ec2_resource()

        instance_list = []
        for instance in ec2.instances.all():
            instance_name = next(
                (x["Value"] for x in instance.tags if x["Key"] == "Name"), None
            )

            if not instance_name:
                continue

            if chosen_type in INSTANCE_TYPES:
                if chosen_type.lower() in instance_name.lower():
                    instance_list.append((instance_name, instance.id))
            else:
                instance_list.append((instance_name, instance.id))

        if not instance_list:
            print("No instances found for your selection")
            sys.exit(1)

        return instance_list

    def _connect_to_instance(self, chosen_instance: str) -> None:
        connection_print = f"{'#' * 5} Connecting to {chosen_instance[0]} {'#' * 5}"
        print("#" * len(connection_print))
        print(connection_print)
        print("#" * len(connection_print))

        os.execlp(
            "aws",
            "aws",
            "ssm",
            "start-session",
            "--target",
            chosen_instance[1],
            "--region",
            self._aws_region,
            "--profile",
            self._profile,
        )

    def connect(self) -> None:
        # Choose region
        chosen_region = menu_picker_util(REGIONS, "Pick your region...")
        self._aws_region = chosen_region.split(" ")[-1]

        # Choose instance type
        chosen_type = menu_picker_util(INSTANCE_TYPES + ["All"], "Pick server type...")

        # Get instances that belong to the selected type
        instance_list = self._get_instances(chosen_type)

        # Choose instance
        chosen_instance = menu_picker_util(
            instance_list, "Pick instance and connect...!"
        )

        # Connect to instance
        self._connect_to_instance(chosen_instance)


if __name__ == "__main__":
    config_file_path = path.join(sys.path[0], "config.json")
    config = config_util(config_file_path)

    session = SSMConnect(config=config)
    session.connect()
