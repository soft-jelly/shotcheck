# SPDX-License-Identifier: MIT
"""ComfyUI entry point: copy this repository into custom_nodes/shotcheck."""

from .shotcheck.node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
