# -*- coding: utf-8 -*-
"""Runner: load single-platform config, then run the FULL v2 chain unchanged.
Separate result file (probe_v2_REAL_results.json); v2.3 synthetic results intact."""
import json, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p2", os.path.join(HERE,"probe_v2.py"))
p2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p2)
cfg = json.load(open(os.path.join(HERE,"real_platform_config.json"),encoding="utf-8"))["mapped_to_model"]
info = p2.configure(cfg)
print("CONFIGURED:", json.dumps(info, ensure_ascii=False))
print("RES =", p2.RES)
print("PER_TM_CALIBRATION =", p2.PER_TM_CALIBRATION,
      "| GAIN_SCALE =", p2.GAIN_SCALE, "| dw_grid_max =", p2.DW_GRID[-1])
p2.main()
