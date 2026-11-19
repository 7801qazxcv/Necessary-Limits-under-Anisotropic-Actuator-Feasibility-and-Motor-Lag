# Baseline set and equal-budget declaration

This short article does **not** claim a new controller, so the baselines below
are verification vehicles used to locate the observed sufficient boundary, not
rivals to be beaten. Every family receives the same tuning budget.

- Four controller families (`qpd`, `smc`, `qpd_ff`, `proposed`) are tuned on the
  same 25-combination gain grid (`KP_GRID` x `KD_GRID`) over three disjoint
  calibration scenes, with an **equal budget** of 25 evaluations per family.
- Calibration is **per motor time constant** on the identified platform: a
  single gain set tuned at the fast constant is not reused at the slow constant,
  because the two differ by a factor of 4.5 and that reuse was measured to
  diverge even at zero impact.
- All families see the same impulse grid, the same disturbance realisations
  (turbulence main arm and adversarial constant arm), the same integration step
  and the same frozen recovery criterion. Disturbances are band-limited and
  matched in RMS across arms.
- The comparison includes cost metrics (saturation duty, peak torque, recovery
  time) so an apparent advantage is reported with its cost, not as a win.
- Paired comparisons are reported with a sign test and Holm correction at family
  alpha 0.05, but these are \emph{descriptive} only: the paired units are
  (direction, motor time constant, controller family) cells from one
  deterministic fixed grid, not independent replicates, so the test carries no
  inferential claim. No Holm survivor is claimed where none exists; on the
  identified platform the proposed family shows no significant advantage and
  this is reported plainly. Multi-seed replication would be required before any
  inferential comparison.
- BLOCKED cells (unstable zero-impact baseline under their own calibrated gains)
  are excluded from all statistics and are never reported as a zero recovery
  boundary. Degenerate non-monotone cells are excluded but retained in artifacts.
