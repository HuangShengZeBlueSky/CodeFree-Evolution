#!/usr/bin/env python3
"""Read the sole experiment MD and execute one explicitly configured command."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import yaml


class UniqueKeys(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in keys:
                raise ValueError(f"Duplicate configuration key: {key}")
            keys.add(key)
        return super().construct_mapping(node, deep=deep)


def load_config(path):
    path = Path(path).resolve()
    raw = path.read_text()
    blocks = re.findall(r"^```yaml experiment-config\s*\n(.*?)^```\s*$", raw, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError("experiment.md must contain exactly one yaml experiment-config block")
    config = yaml.load(blocks[0], Loader=UniqueKeys)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    dispatched_path = os.environ.get("EXPERIMENT_CONFIG_RECORD")
    dispatched_sha = os.environ.get("EXPERIMENT_CONFIG_SHA256")
    if dispatched_path and Path(dispatched_path).resolve() == path and dispatched_sha and sha != dispatched_sha:
        raise ValueError("Experiment MD changed after dispatch; use a new configuration identity")
    required = {"schema_version", "experiment_id", "workdir", "environment", "roles",
                "benchmark", "harness", "search", "scoring", "limits", "artifacts", "commands"}
    if not isinstance(config, dict) or required - config.keys():
        raise ValueError("Experiment MD is missing required sections")
    if config["schema_version"] != 1:
        raise ValueError("Unsupported experiment configuration version")
    for key in required - {"schema_version", "experiment_id", "workdir"}:
        if not isinstance(config[key], dict):
            raise ValueError(f"{key} must be a mapping")
    if not Path(config["workdir"]).is_absolute() or not Path(config["workdir"]).is_dir():
        raise ValueError("workdir must be an existing absolute directory")
    if not config["experiment_id"] or not config["commands"]:
        raise ValueError("experiment_id and commands must be explicit")
    for name, command in config["commands"].items():
        if not isinstance(command, dict):
            raise ValueError(f"Command {name} must be a mapping")
        argv = command.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            raise ValueError(f"Command {name} requires a nonempty argv string array")
        timeout = command.get("timeout_seconds")
        if type(timeout) not in (int, float) or timeout <= 0:
            raise ValueError(f"Command {name} requires an explicit positive timeout_seconds")
    return config, sha


def run_command(path, command_name, variables):
    path = Path(path).resolve()
    config, sha = load_config(path)
    if command_name not in config["commands"]:
        raise ValueError(f"No configured command named {command_name}")
    values = {"config_record": str(path), "config_sha256": sha, **variables}
    def replace(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f"Missing command input: {key}")
        return values[key]
    command = config["commands"][command_name]
    argv = [re.sub(r"\{([a-zA-Z_][a-zA-Z_0-9]*)\}", replace, arg) for arg in command["argv"]]
    env = dict(os.environ)
    for key, value in config["environment"].items():
        if isinstance(value, dict) and set(value) == {"from_env"}:
            if value["from_env"] not in os.environ:
                raise ValueError(f"Required environment variable is missing for {key}")
            env[key] = os.environ[value["from_env"]]
        elif isinstance(value, str):
            env[key] = value
        else:
            raise ValueError(f"Environment {key} must be a string or from_env reference")
    env["EXPERIMENT_CONFIG_RECORD"] = str(path)
    env["EXPERIMENT_CONFIG_SHA256"] = sha
    result = subprocess.run(argv, cwd=config["workdir"], env=env,
                            timeout=command["timeout_seconds"], check=False)
    print(json.dumps({"experiment_id": config["experiment_id"], "config_sha256": sha,
                      "command": command_name, "exit_code": result.returncode}), flush=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--command")
    parser.add_argument("--set", action="append", default=[])
    args = parser.parse_args()
    if not args.command:
        config, sha = load_config(args.config)
        print(json.dumps({"experiment_id": config["experiment_id"], "config_sha256": sha,
                          "commands": sorted(config["commands"])}))
        return
    variables = {}
    for raw in args.set:
        key, sep, value = raw.partition("=")
        if not sep or not key or key in variables or key in {"config_record", "config_sha256"}:
            raise ValueError("--set requires a unique key=value; configuration identity is reserved")
        variables[key] = value
    raise SystemExit(run_command(args.config, args.command, variables))


if __name__ == "__main__":
    main()
