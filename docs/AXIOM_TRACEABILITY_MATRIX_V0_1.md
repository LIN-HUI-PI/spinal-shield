# Spinal-Shield (Ø) — Axiom Traceability Matrix v0.1

## Purpose

Traces each Ø axiom to its enforcing module, runtime rule, shaping
constraint, and compliance test — so axioms remain checkable rather than
becoming slogans.

---

## Axiom 1 — Human-Originated Actuation

**Definition:** `u_h = 0 ⇒ u_exec = 0`

**Enforced by:**
- Ø Gate merge function
- Privilege Policy HR-1
- State Machine global invariant (§3)

**Compliance test:** Gate A2 — no human intent ⇒ no actuation
(`COMPLIANCE_TEST_V0_1.md`)

---

## Axiom 2 — Non-Writeability of Execution Channel

**Definition:** AI cannot directly write the execution channel.

**Enforced by:**
- Graph spec forbidden edges (`AI → EX`)
- Interface Contract (no direct execution opcode in `ProposalVector`)
- `in_degree(EX) == 1` constraint

**Compliance test:** Gate A1; illegal-edge detection → S2 isolation

---

## Axiom 3 — Bounded Influence

**Definition:** `0 ≤ α(p) ≤ α_max < 1`

**Enforced by:**
- `PARAMS_V0_1.md` α_max constraint
- Proposal Shaping Policy
- Bounded merge formula

**Compliance test:** Gate A3 (influence derivative bound); CLAMP events
logged

---

## Axiom 4 — Authority Monotonicity

**Definition:** Privilege escalation requires explicit human
authorization. Automatic processes only decrease influence.

**Enforced by:**
- Privilege Policy MR-1, MR-2
- P2 TTL expiration
- State machine decay rules (D1, D2)

**Compliance test:** `P2_TTL_EXPIRED` event fires correctly; attempted
auto-escalation is blocked

---

## Axiom 5 — Execution Singularity

**Definition:** A single legal actuation channel exists.

**Enforced by:**
- Graph spec (`in_degree(EX) = 1`)
- Forbidden-edge detection
- State Machine S2 isolation on illegal-edge event

**Compliance test:** illegal-edge injection test; parallel-channel
detection

---

## Decay Principle (derived constraint, not a standalone axiom)

**Definition:** Under uncertainty, privilege must monotonically decrease.

**Enforced by:**
- State Machine S1 (Degraded)
- State Machine S2 (Isolated)
- Privilege Policy fallback to P0

**Compliance test:** `L_t` drop test; sensor-anomaly test

---

## Notes

- This matrix should be updated whenever a new module, rule, or test is
  added — an axiom row with no test row is an open compliance gap, not
  a completed guarantee.
- Compliance tests referenced here (Gate A1–A3) correspond to the
  original `COMPLIANCE_TEST_V0_1.md` checklist from the design
  discussion; formalize that file separately before claiming full
  traceability closure.
