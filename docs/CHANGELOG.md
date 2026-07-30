# Changelog

Tracks structural and substantive changes across the whole Spinal-Shield
(Ø) repository, not just simulation versions.

---

## v1.1 (draft, not yet released to GitHub/Zenodo)

Prompted by re-reviewing the original design conversation for gaps that
didn't carry through into the v1.0 formalization.

- **Added Axiom 0 — Reflex Sovereignty.** The original design discussion
  included a "Layer 3 — Emergency Reflex Override" concept (pain
  withdrawal, overload protection, fatigue shutdown must bypass AI
  entirely) that did not survive the evolution from the early
  three-layer sketch into the final three-domain + Ø Gate architecture.
  Re-added as a standalone axiom, positioned before I1 because it
  outranks the human-originated-actuation framing itself — reflexes
  fire faster than `u_h(t)` can even be computed. This is a categorical
  (topological) exclusion, not an α-bounded permission like I1–I4.
- **Added I5 — Bystander Physical Safety.** Identified during the same
  review: the threat model only ever covered protecting the *user* from
  AI overreach, never protecting *bystanders* from unintended physical
  contact. Scoped narrowly and deliberately: covers only unintentional
  contact due to insufficient sensing, addressed via a `PROX` limiter
  node. Explicitly does NOT cover intentional misuse by the user
  (considered and rejected — see rationale below) or identity/background
  -based access control (also considered and rejected).
- **Resolved a topological tension**: Axiom 0 requires a path to the
  actuator that bypasses the Ø Gate; Axiom 5 (Execution Singularity)
  requires `EX` to have exactly one predecessor. Resolved by clarifying
  that `RFX` connects to physical actuator hardware below/outside the
  layer `EX` and Axiom 5 govern — Axiom 5's guarantee is about the
  single *AI-mediated* command path, not the reflex arc. See
  `docs/GRAPH_SPEC_V0_1.md` for the full explanation and the resulting
  constraint that Axiom 0 compliance requires genuine hardware
  separation, not just a software flag.
- **Explicitly rejected**: identity/criminal-history-based access
  control as a mechanism for protecting bystanders. Considered and
  rejected on both architectural grounds (couples a resource-authority
  system to an unrelated identity-adjudication system) and normative
  grounds (pre-emptive restriction based on background rather than
  in-the-moment behavior). Recorded in
  `docs/SPINAL_SHIELD_OVERVIEW.md` §1 "Out of scope" so the reasoning
  isn't lost if the question resurfaces.
- **Known gap, not yet closed:** neither Axiom 0 nor I5 has a
  compliance test yet — both require a hardware or embodied-simulation
  layer that the current 1D scalar simulation (v0.3) does not have.
  Flagged in `docs/AXIOM_TRACEABILITY_MATRIX_V0_1.md`.
- **Corrected the justification for Axiom 0** after external review: the
  original draft justified the exclusion by appeal to reflex latency
  ("gate-mediated latency would be too slow"), which incorrectly implied
  the exclusion was an engineering-performance question. Corrected to
  state plainly that this is an authority-boundary decision — AI has no
  standing to participate regardless of how fast it could act.
- **Added an explicit open question**: who classifies a given behavior
  as a "reflex" (Axiom 0, full exclusion) versus a bounded safety
  behavior (I5) versus an ordinary AI-assistable task (I1–I4)? Cases
  like grip-force limiting or exoskeleton fall-protection are not
  obviously biological reflexes. Not resolved in v1.1 — left as an
  explicit open item in `docs/SPINAL_SHIELD_OVERVIEW.md` rather than
  silently assumed away.
- **Flagged a second gap in Axiom 0** after further external review:
  the axiom as written only governs Runtime Authority (can AI
  participate in a reflex decision during operation?), not
  Configuration Authority (can the reflex pathway's own thresholds,
  routing, firmware, or calibration be modified outside operation, and
  by whom?). A system could be Axiom-0-compliant at runtime while still
  vulnerable to AI-mediated tampering during a maintenance/configuration
  window. Documented as an explicit, unresolved scope boundary in
  `docs/SPINAL_SHIELD_OVERVIEW.md` rather than specified prematurely —
  a full Configuration Authority model (factory/certified-service
  process, AI's role if any in proposing changes, independent audit
  mechanism) is deferred to a future version.

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
