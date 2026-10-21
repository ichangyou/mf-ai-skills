import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_plan.py"
spec = importlib.util.spec_from_file_location("mab_check_plan_test_module", SCRIPT)
check_plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_plan)


def task(tid, feature="F001", priority="P0", deps=()):
    return {"id": tid, "title": tid, "feature_id": feature, "priority": priority, "status": "PENDING",
            "dependencies": list(deps), "acceptance": ["works"], "verification": ["unit test"]}


def plan(tasks, features=None):
    return {"features": features or [{"id": "F001", "name": "Create task", "priority": "P0"}], "tasks": tasks}


class CheckPlanTest(unittest.TestCase):
    def test_valid_plan_returns_dependency_order(self):
        errors, warnings, order = check_plan.check(plan([task("T002", deps=["T001"]), task("T001")]), "F001")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(order, ["T001", "T002"])

    def test_cycle_is_reported(self):
        errors, _, order = check_plan.check(plan([task("T001", deps=["T002"]), task("T002", deps=["T001"])]), "F001")
        self.assertTrue(any("circular" in e for e in errors))
        self.assertEqual(order, [])

    def test_missing_dependency_and_duplicate_id(self):
        errors, _, _ = check_plan.check(plan([task("T001", deps=["T009"]), task("T001")]), "F001")
        self.assertIn("T001: depends on missing task T009", errors)
        self.assertIn("duplicate task id T001", errors)

    def test_p0_feature_needs_task_and_acceptance(self):
        features = [{"id": "F001", "name": "a", "priority": "P0"}, {"id": "F002", "name": "b", "priority": "P0"}]
        errors, _, _ = check_plan.check(plan([task("T001")], features), "F001 only")
        self.assertIn("F002: P0 feature has no task", errors)
        self.assertIn("F002: P0 feature is not referenced in docs/ACCEPTANCE.md", errors)

    def test_task_without_verification_fails(self):
        bad = task("T001")
        bad["verification"] = []
        errors, _, _ = check_plan.check(plan([bad]), "F001")
        self.assertIn("T001: missing verification", errors)

    def test_p0_depending_on_p1_is_warning(self):
        features = [{"id": "F001", "name": "a", "priority": "P0"}, {"id": "F002", "name": "b", "priority": "P1"}]
        tasks = [task("T001", deps=["T002"]), task("T002", feature="F002", priority="P1")]
        errors, warnings, _ = check_plan.check(plan(tasks, features), "F001")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, ["T001: P0 task depends on P1 task T002"])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tasks").mkdir()
            (root / "docs").mkdir()
            (root / "tasks" / "tasks.json").write_text(json.dumps(plan([task("T001")])), encoding="utf-8")
            (root / "docs" / "ACCEPTANCE.md").write_text("## F001\n- works\n", encoding="utf-8")
            ok = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout)
            self.assertIn("PASSED", ok.stdout)
            (root / "docs" / "ACCEPTANCE.md").unlink()
            bad = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("missing docs/ACCEPTANCE.md", bad.stdout)


if __name__ == "__main__":
    unittest.main()
