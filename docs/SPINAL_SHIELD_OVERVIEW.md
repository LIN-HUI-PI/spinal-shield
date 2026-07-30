# Project Spinal-Shield (Ø) — Overview v1.1

> **v1.1 changes:** Added Axiom 0 (Reflex Sovereignty) — a categorical,
> non-bounded exclusion for physiological reflex pathways, distinct from
> the α-bounded Ø Gate invariants below. Added bystander physical-safety
> threat model entry (unintentional contact only — see §1). See
> `CHANGELOG.md` for full rationale.

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
- **Unintentional physical contact with bystanders** — the actuator
  moving through physical space and making unplanned contact with a
  person other than the user, due to insufficient environmental sensing
  (not due to user intent). In scope as a *behavioral/physical* hazard,
  addressed via proximity sensing and force limiting at the Execution
  Domain (see §4, I5).

### Out of scope

- Offensive deception systems (decoys, fake telemetry meant to mislead
  monitoring).
- Destructive or self-harmful mechanisms (device "self-destruct",
  "molecular degradation", etc).
- **Identity-based access control** (e.g. restricting who may use the
  system based on criminal history or other background attributes).
  Spinal-Shield governs execution authority *during* use by an already-
  authorized user; it does not — and should not — attempt to adjudicate
  who is authorized to use the underlying device. That is a deployment-
  policy and legal question, out of scope for an execution-authority
  architecture, and any such gating belongs (if anywhere) at a layer
  entirely outside this specification.
- **Intentional misuse by an authorized user** (a user deliberately
  directing the device to harm a third party). This is a behavior-of-the-
  person problem, not a structural AI-authority problem, and is not
  addressed by the Ø Gate's mechanisms — see the distinction drawn in
  I5 below.

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

## 3. Axiom 0 — Reflex Sovereignty (precedes the Ø Gate)

Certain physiological reflex pathways (e.g. pain withdrawal, overload
protection, fatigue shutdown) MUST bypass the Ø Gate, the Compute
Domain, and the Proposal Buffer **entirely**.

These pathways are **not** subject to α-bounding, privilege tiering, or
any gate-mediated judgment. Participation by the AI system in this
pathway — at any influence level, including near-zero — is categorically
forbidden. This is a **topological exclusion**, not a bounded permission:
the exclusion is an authority-boundary decision, not a latency-adequacy
one. That is, this is not a claim that gate-mediated judgment would be
"too slow" — a sufficiently fast gate could, in principle, meet any
given latency requirement. The claim is that AI has no standing to
participate in this decision at all, regardless of how fast it could do
so. (An earlier draft of this axiom justified the exclusion by appeal to
latency; that framing was incorrect and has been corrected, since it
implied the exclusion was contingent on engineering performance rather
than categorical.)

Axiom 0 is listed before I1 because it outranks the human-originated-
actuation framing itself: a reflex fires faster than, and independently
of, the Intent Domain's `u_h(t)` being computed at all.

**Implementation note:** `RFX` (see `GRAPH_SPEC_V0_1.md`) denotes any
AI-unreachable pathway satisfying this axiom — a fully separate hardwired
circuit is one way to satisfy it, but so is a dedicated safety
microcontroller that the Compute Domain has no access to. What Axiom 0
requires is that AI has no modification or observation access to this
path, not a specific implementation technology.

**Open question, not resolved by this specification:** who decides what
qualifies as a "reflex" under Axiom 0, versus a bounded safety behavior
under I5, versus an ordinary AI-assistable control task under I1–I4?
Pain withdrawal is an uncontroversial case. Grip-force limiting in a
prosthetic hand, or fall-protection response in an exoskeleton, are not
obviously biological reflexes and their classification is currently
undefined. A future revision should define a Reflex Classification
scheme (e.g. distinguishing biological / mechanical / safety / learned
reflexes) before this axiom can be claimed as fully specified for a
given deployment. Until then, classification is left to the specific
implementation, which must document its reasoning.

**Scope boundary: Runtime Authority vs. Configuration Authority.**
Axiom 0 as stated above governs **Runtime Authority only** — whether AI
may participate in a reflex decision *during operation*. It does not
address **Configuration Authority** — whether the reflex pathway's own
parameters, thresholds, routing, firmware, or calibration may be
modified *outside* operation, and if so, by whom and under what
procedure. These are different questions: a system could satisfy Axiom
0 perfectly (AI touches nothing at runtime) while still being
compromised if AI-controlled tooling can silently rewrite the reflex
threshold during a maintenance window. Spinal-Shield v1.1 does **not**
yet specify Configuration Authority for the reflex pathway — this is an
explicit, acknowledged gap, not an oversight papered over. A future
version should define, at minimum: (a) whether reflex-path
configuration is modifiable at all outside a factory/certified-service
process, (b) whether the Compute Domain may have any role even in
*proposing* such changes, and (c) how modifications are authenticated
and audited independently of the Ø Gate's runtime mechanisms (since the
Gate has no jurisdiction here by definition). Until specified, no
implementation should claim Axiom 0 compliance covers configuration-time
integrity — only runtime non-participation.

*Design note:* this axiom currently covers motor/actuation reflexes.
Autonomic signals (respiration, cardiac rhythm) are not currently in
scope — see `PARAMS_V0_1.md` for the scope boundary if this
architecture is later applied to a system involving such signals.

---

## 4. Ø Invariants (MUST)

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
- **I5 — Bystander Physical Safety (behavioral, not identity-based)**:
  The Execution Domain MUST incorporate proximity/force sensing to
  prevent unintended actuator contact with persons other than the
  authorized user. This is a physical-safety control on *behavior in
  space*, independent of who the user is or what AI privilege tier is
  active — it applies identically at P0, P1, and P2. It does not extend
  to preventing intentional misuse by the user (see §1, Out of scope).

---

## 5. Phase-1 Deliverables

- **Phase-1A: Embodied Liveness Gate** — computes liveness confidence
  L_t and session binding tag B_t; drives privilege levels for proposals.
- **Phase-1B: Unidirectional Execution Gate** — proposal buffer only;
  execution channel write is human-only.
- **Phase-1C: Non-Deceptive Anti-Exfiltration** — detect abnormal access
  patterns; downgrade / isolate / minimal-disclosure responses; audit
  logging.

---

## 6. Success Criteria (Engineering)

- Demonstrable: AI cannot actuate without human intent (I2).
- Demonstrable: AI cannot increase influence beyond α_max (I3).
- Demonstrable: Liveness failures cause safe downgrade (Phase-1A).
- Demonstrable: Suspicious access triggers isolation (Phase-1C).
- Auditable: all gate decisions are logged with verifiable integrity
  (without exposing raw intent).

---

## 7. Notation (Minimal)

- `u_h(t)`: human intent signal (authorized control parameters)
- `u_ai(t)`: AI proposal vector
- `L_t`: liveness confidence (0..1)
- `B_t`: session binding tag (non-reversible binding)
- `α`: AI influence gain
- `u_exec(t)`: final execution command

---

## 8. Reference Linkage

- Asymmetric Authority Architecture and Executable Authority (parent
  axioms) — DOI: 10.5281/zenodo.21384892
- NOIRÉA R1–R4: constraints on cross-session representation persistence.
- Decision Mirror: optional policy layer for human-authorized
  confirmations.
