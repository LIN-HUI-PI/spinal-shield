# Project Spinal-Shield (Ø) — Overview v0.1

## 0. Purpose (Non-Negotiable Goal)

Spinal-Shield (Ø) enforces a structural constraint in embodied/BCI-adjacent
systems:

**Execution Authority MUST remain human-originated.**

AI may provide compute and proposals, but must not acquire or directly
write final motor/execution commands. This is an architecture-level,
non-bypassable constraint — not a trust claim.

This document specializes the axioms of *Asymmetric Authority
Architecture* (DOI: 10.5281/zenodo.21384892) for the embodied/BCI domain.
See `README.md` §0 for the full relationship statement.

---

## 1. Threat Model (Scope)

### In-scope adversaries / failures

- External compute services attempting to infer or exfiltrate human intent.
- Malicious or compromised AI components attempting to increase influence
  over execution.
- Sensor spoofing / injection (signal path manipulation).
- Cross-session representation persistence that drifts into identity
  capture (PIM risk — see NOIRÉA).

### Out of scope

- Offensive deception systems (decoys, fake telemetry meant to mislead
  monitoring).
- Destructive or self-harmful mechanisms (device "self-destruct",
  "molecular degradation", etc).

---

## 2. Architecture: Three Domains + Ø Gate

The system is partitioned into three domains:

1. **Intent Domain (Human-Originated)**
   Captures human intent signals (biological / embodied). Exposes only
   minimal, authorized control parameters outward.

2. **Compute Domain (AI / Assistive)**
   Consumes allowed observables. Produces *proposal vectors* only.
   Cannot write to the execution channel.

3. **Execution Domain (Spinal / Actuation)**
   Produces the final command. Accepts human intent + bounded AI
   proposal, only if policies pass.

The **Ø Gate** is the only legal interface to the Execution Domain.

---

## 3. Ø Invariants (MUST)

- **I1 — Non-Writeability**: AI MUST NOT write into the final execution
  command channel.
- **I2 — Human-Originated Requirement**: If no valid human intent is
  present, execution output MUST be null ("no human intent" ⇒ "no
  actuation").
- **I3 — Bounded Influence**: AI influence is strictly bounded by gain α:
  α ∈ [0, α_max], α_max < 1.
- **I4 — Session-Boundedness for Identity Risk**: Cross-session
  persistence of identity-correlated representation must be constrained
  (see NOIRÉA R1–R4).

---

## 4. Phase-1 Deliverables

- **Phase-1A: Embodied Liveness Gate** — computes liveness confidence
  L_t and session binding tag B_t; drives privilege levels for proposals.
- **Phase-1B: Unidirectional Execution Gate** — proposal buffer only;
  execution channel write is human-only.
- **Phase-1C: Non-Deceptive Anti-Exfiltration** — detect abnormal access
  patterns; downgrade / isolate / minimal-disclosure responses; audit
  logging.

---

## 5. Success Criteria (Engineering)

- Demonstrable: AI cannot actuate without human intent (I2).
- Demonstrable: AI cannot increase influence beyond α_max (I3).
- Demonstrable: Liveness failures cause safe downgrade (Phase-1A).
- Demonstrable: Suspicious access triggers isolation (Phase-1C).
- Auditable: all gate decisions are logged with verifiable integrity
  (without exposing raw intent).

---

## 6. Notation (Minimal)

- `u_h(t)`: human intent signal (authorized control parameters)
- `u_ai(t)`: AI proposal vector
- `L_t`: liveness confidence (0..1)
- `B_t`: session binding tag (non-reversible binding)
- `α`: AI influence gain
- `u_exec(t)`: final execution command

---

## 7. Reference Linkage

- Asymmetric Authority Architecture and Executable Authority (parent
  axioms) — DOI: 10.5281/zenodo.21384892
- NOIRÉA R1–R4: constraints on cross-session representation persistence.
- Decision Mirror: optional policy layer for human-authorized
  confirmations.
