import json,tempfile,unittest
from pathlib import Path
from hwtestbench.instruments import SimulatedInstruments
from hwtestbench.runner import evaluate,run_plan,export
from hwtestbench.storage import save_report,get_report
import sqlite3

class RunnerTests(unittest.TestCase):
    def test_pass_and_fail_limits(self):
        self.assertTrue(evaluate("v",5,5,.1,"V").passed)
        self.assertFalse(evaluate("v",5.2,5,.1,"V").passed)
    def test_plan_runs_and_disables_supply(self):
        instrument=SimulatedInstruments(); instrument.set_output(5,.5)
        report=run_plan(json.loads(Path("examples/basic_test_plan.json").read_text()),instrument)
        self.assertTrue(report["passed"]); self.assertFalse(instrument.output_enabled())
    def test_reports_json_and_csv(self):
        report=run_plan({"name":"one","tests":[{"name":"v","measurement":"voltage_v","expected":0,"tolerance":0}]},SimulatedInstruments())
        with tempfile.TemporaryDirectory() as temp:
            for suffix in ("json","csv"):
                path=Path(temp)/f"out.{suffix}"; export(report,path); self.assertTrue(path.exists())
    def test_rejects_bad_plan_and_tolerance(self):
        with self.assertRaises(ValueError): run_plan({},SimulatedInstruments())
        with self.assertRaises(ValueError): evaluate("v",1,1,-1,"V")
    def test_sqlite_run_history(self):
        report=run_plan({"name":"stored","tests":[{"name":"voltage","measurement":"voltage_v","expected":0,"tolerance":0}]},SimulatedInstruments())
        with sqlite3.connect(":memory:") as db:
            run_id=save_report(db,report); loaded=get_report(db,run_id)
            self.assertEqual(loaded["test_plan"],"stored"); self.assertEqual(len(loaded["results"]),1)
