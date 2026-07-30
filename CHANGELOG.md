# Changelog

Tracks structural and substantive changes across the whole Spinal-Shield
(Ø) repository, not just simulation versions.

---

## Repository Structure

- Consolidated all files into `docs/` (architecture spec) and
  `simulations/` (empirical validation), with `simulations/archive/`
  for superseded material. See `README.md` §9 for the filing rule.

---

## Simulation Results

### v0.3 (current)
- Replaced oracle-based decay trigger (`|u_ai| vs |u_h|` comparison,
  not available to a real system) with a self-referential rate-anomaly
  detector on the AI proposal channel's own statistics — consistent
  with `RATE_ANOMALY_MILD/SEVERE` in `docs/PRIVILEGE_POLICY_V0_1.md`.
- Changed default operating point from `α_max` to `α1` (P1 tier),
  since no `auth_event` is modeled and the system should not default
  near the P2 ceiling without authorization.
- Added a control test (constant, non-escalating AI proposal) to
  confirm the detector does not suppress benign behavior — this is
  what makes the attack-mode suppression results meaningful.
- Result: max R(t) across all four escalation modes dropped further
  (0.017–0.020) versus v0.2 (0.221–0.245), while removing the oracle
  dependency.

### v0.2 (archived)
- Fixed a metric-definition bug in v0.1: R(t) was computed using
  unclamped `u_ai` divided by a `1e-5` floor at human-intent
  zero-crossings, producing spurious spikes up to ~66,000 that
  contradicted the v0.1 conclusion. Independent re-run of the original
  v0.1 code confirmed R(t) actually breached the 1.0 threshold in
  4.6%–9.7% of timesteps — the physical execution signal (`u_exec`)
  was correctly bounded throughout; only the R(t) visualization metric
  was broken.
- Fix: R(t) now reflects realized (post-clamp, post-α) contribution to
  execution, masked to 0 rather than divided by a near-zero floor when
  `|u_h|` is below threshold.
- Did not yet address the oracle-comparison issue in the decay trigger
  (fixed in v0.3).

### v0.1 (superseded, not separately filed)
- Original Gemini-authored demo and results document. Established the
  core simulation structure (No-Gate baseline vs. Ø-Gate bounded merge,
  four escalation modes) but contained the R(t) metric bug described
  above. Superseded in full by v0.2 and v0.3; kept only as a note here
  for audit-trail completeness, since the original file was not
  independently saved before the bug was identified.

---

## Architecture Documents

- Initial v1.0 skeleton established: Overview, Graph Spec, Interface
  Contract, Privilege Policy, Proposal Shaping Policy, Gate State
  Machine, Params Registry, Axiom Traceability Matrix, Compliance Test.
- README's opening section reframed to explicitly position Spinal-Shield
  as a domain-specific instantiation of *Asymmetric Authority
  Architecture and Executable Authority* (DOI: 10.5281/zenodo.21384892)
  rather than an independent axiom set, to avoid redundant-contribution
  concerns in future publication.
