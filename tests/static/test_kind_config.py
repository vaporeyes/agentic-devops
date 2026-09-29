# ABOUTME: Guards the local kind cluster definition: node image pinned by digest, at or above floor.
# ABOUTME: Prevents kind's release default from silently choosing the Kubernetes version.
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
KIND_CONFIG = REPO_ROOT / "platform" / "profiles" / "local" / "kind-config.yaml"
IMAGE = re.compile(r"^kindest/node:v(\d+)\.(\d+)\.\d+@sha256:[0-9a-f]{64}$")


def _floor() -> tuple[int, int]:
    metadata = yaml.safe_load((REPO_ROOT / "components.yaml").read_text())["metadata"]
    major, minor = metadata["kubernetes_min_minor"].split(".")
    return int(major), int(minor)


def test_every_node_image_is_digest_pinned_and_supported():
    nodes = yaml.safe_load(KIND_CONFIG.read_text())["nodes"]
    assert nodes, "kind config defines no nodes"
    for node in nodes:
        match = IMAGE.match(node.get("image", ""))
        assert match, f"node image not pinned by digest: {node.get('image')!r}"
        version = (int(match.group(1)), int(match.group(2)))
        assert version >= _floor(), f"{node['image']} below floor {_floor()}"
