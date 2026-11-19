import unittest
from dataclasses import FrozenInstanceError

from infra_agent.models import MAX_LOG_LINES, Bundle


class BundleBasics(unittest.TestCase):
    def test_defaults(self):
        b = Bundle(name="web", status="running")
        self.assertIsNone(b.exit_code)
        self.assertFalse(b.oom_killed)
        self.assertEqual(b.restart_count, 0)
        self.assertIsNone(b.health)
        self.assertEqual(b.error, "")
        self.assertEqual(b.logs, ())

    def test_is_frozen(self):
        b = Bundle(name="web", status="running")
        with self.assertRaises(FrozenInstanceError):
            b.status = "exited"


class FromInspect(unittest.TestCase):
    SAMPLE = [
        {
            "Name": "/panic-room-api-1",
            "RestartCount": 2,
            "State": {
                "Status": "Running",
                "ExitCode": 0,
                "OOMKilled": False,
                "Error": "",
                "Health": {"Status": "healthy"},
            },
        }
    ]

    def test_parses_list_and_strips_slash(self):
        b = Bundle.from_inspect(self.SAMPLE, "line one\n\nline two\n")
        self.assertEqual(b.name, "panic-room-api-1")
        self.assertEqual(b.status, "running")  # lowercased
        self.assertEqual(b.restart_count, 2)
        self.assertEqual(b.health, "healthy")
        self.assertEqual(b.logs, ("line one", "line two"))  # blank line dropped

    def test_accepts_bare_dict(self):
        b = Bundle.from_inspect(self.SAMPLE[0])
        self.assertEqual(b.name, "panic-room-api-1")

    def test_missing_health_is_none(self):
        sample = [{"Name": "/x", "State": {"Status": "running"}}]
        self.assertIsNone(Bundle.from_inspect(sample).health)

    def test_oom_flag_is_parsed(self):
        sample = [{"Name": "/x", "State": {"Status": "exited", "ExitCode": 137, "OOMKilled": True}}]
        b = Bundle.from_inspect(sample)
        self.assertTrue(b.oom_killed)
        self.assertEqual(b.exit_code, 137)

    def test_name_falls_back_to_short_id(self):
        b = Bundle.from_inspect({"Id": "abcdef1234567890", "State": {}})
        self.assertEqual(b.name, "abcdef123456")
        self.assertEqual(b.status, "unknown")

    def test_logs_truncated_to_last_lines(self):
        logs = "\n".join(f"l{i}" for i in range(MAX_LOG_LINES + 20))
        b = Bundle.from_inspect(self.SAMPLE, logs)
        self.assertEqual(len(b.logs), MAX_LOG_LINES)
        self.assertEqual(b.logs[-1], f"l{MAX_LOG_LINES + 19}")

    def test_empty_inspect_raises(self):
        with self.assertRaises(ValueError):
            Bundle.from_inspect([])


if __name__ == "__main__":
    unittest.main()
