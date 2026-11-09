import argparse,json
from pathlib import Path
from .instruments import SimulatedInstruments
from .runner import run_plan,export

def main():
    p=argparse.ArgumentParser(description="Run a JSON test plan against deterministic simulated instruments")
    p.add_argument("plan",nargs="?",default="examples/basic_test_plan.json"); p.add_argument("--json",default="reports/latest.json"); p.add_argument("--csv",default="reports/latest.csv"); a=p.parse_args()
    plan=json.loads(Path(a.plan).read_text(encoding="utf-8")); instrument=SimulatedInstruments(); instrument.set_output(**plan.get("supply",{"voltage_v":5.0,"current_limit_a":.5}))
    report=run_plan(plan,instrument); export(report,a.json); export(report,a.csv)
    print(json.dumps(report,indent=2))
    if not report["passed"]: raise SystemExit(1)

if __name__=="__main__": main()
