"""Tests for OpenMediaVault Compose response normalization."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).parents[1] / "custom_components" / "openmediavault" / "compose.py"
)
SPEC = importlib.util.spec_from_file_location("openmediavault_compose", MODULE_PATH)
COMPOSE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(COMPOSE)


class NormalizeComposeStateTests(unittest.TestCase):
    """Verify state normalization across OMV/Docker formats."""

    def test_running_states(self):
        self.assertEqual(COMPOSE.normalize_compose_state("Up 2 hours"), "running")
        self.assertEqual(COMPOSE.normalize_compose_state("running"), "running")

    def test_specific_non_running_states(self):
        self.assertEqual(
            COMPOSE.normalize_compose_state("Restarting (1)"), "restarting"
        )
        self.assertEqual(COMPOSE.normalize_compose_state("Paused"), "paused")
        self.assertEqual(COMPOSE.normalize_compose_state("Created"), "created")
        self.assertEqual(COMPOSE.normalize_compose_state("Dead"), "dead")
        self.assertEqual(COMPOSE.normalize_compose_state("Down"), "exited")


class ParseComposeOutputTests(unittest.TestCase):
    """Verify parsing and validation of background-job output."""

    def test_parses_current_omv_response(self):
        raw = json.dumps(
            {
                "data": [
                    {
                        "name": "cloud",
                        "uuid": "project-uuid",
                        "status": "Up 3 minutes",
                        "image": "example/cloud:latest",
                        "description": "Cloud stack",
                        "svcname": "cloud",
                        "filedate": "2026-09-28",
                    }
                ],
                "total": 1,
            }
        )

        self.assertEqual(
            COMPOSE.parse_compose_background_output(raw),
            [
                {
                    "name": "cloud",
                    "uuid": "project-uuid",
                    "state": "running",
                    "image": "example/cloud:latest",
                    "project": "Cloud stack",
                    "service": "cloud",
                    "created": "2026-09-28",
                }
            ],
        )

    def test_skips_non_object_rows(self):
        self.assertEqual(
            COMPOSE.parse_compose_background_output('{"data": [null, "bad"]}'),
            [],
        )

    def test_rejects_invalid_shapes(self):
        with self.assertRaises(ValueError):
            COMPOSE.parse_compose_background_output("[]")
        with self.assertRaises(ValueError):
            COMPOSE.parse_compose_background_output('{"data": {}}')


if __name__ == "__main__":
    unittest.main()
