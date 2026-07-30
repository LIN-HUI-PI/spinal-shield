# Spinal-Shield (Ø)
## Execution Authority Architecture for Embodied AI Systems

---

## 0. Relationship to Prior Work

Spinal-Shield (Ø) is a domain-specific reference implementation of the
Execution Authority principles established in *Asymmetric Authority
Architecture and Executable Authority*
(Lin, 2026, DOI: 10.5281/zenodo.21384892).

The parent work defines the general axioms of human-originated control
and bounded AI influence. Spinal-Shield instantiates these axioms for
embodied AI and BCI-adjacent systems, specifying:

- the concrete topology (domains, forbidden edges),
- privilege tiers (P0 / P1 / P2),
- proposal shaping constraints,
- a four-state authority decay machine.

**This repository does not propose new foundational axioms. It extends
and operationalizes existing ones.**

Related work in the same research programme (NOIRÉA / LIN System):

- Asymmetric Authority Architecture and Executable Authority — DOI: 10.5281/zenodo.21384892
- HÚPLŃ v2 (three-variable A-B-Q system) — DOI: 10.5281/zenodo.21093064
- IMLAIS v1.1 — DOI: 10.5281/zenodo.20129845

---

## 1. Overview

Spinal-Shield (Ø) is a reference architecture designed to enforce
structural execution-authority constraints in embodied or
BCI-adjacent AI systems.

Its central principle:

> Execution Authority MUST remain human-originated.

AI systems may provide computation, prediction, and proposals.
They must not directly acquire or write final actuation commands.

This is an architectural constraint, not a policy assumption.

---

## 2. Motivation

As adaptive AI systems integrate with physical and embodied environments,
new structural risks emerge:

- Gradual increase of AI influence over actuation.
- Cross-session representation drift.
- Indirect control-path bypass.
- Privilege escalation without explicit authorization.

Traditional safety approaches focus on alignment and monitoring.
Spinal-Shield enforces **topological non-bypassability** at the
execution layer.

---

## 3. Core Invariants (Ø Axioms)

1. **Human-Originated Actuation**
   If no valid human intent exists, no actuation is produced.

2. **Non-Writeable Execution Channel**
   AI components cannot directly write to the execution channel.

3. **Bounded Influence**
   AI contribution is strictly limited by α, where 0 ≤ α < 1.

4. **Authority Monotonicity**
   Privilege may automatically decrease. Escalation requires explicit
   human authorization.

5. **Execution Singularity**
   A single legal actuation path exists. Parallel or shadow actuation
   channels are forbidden.

*(These are inherited from the parent Asymmetric Authority Architecture;
see Section 0.)*

---

## 4. Architectural Domains

- Intent Domain (Human-Originated)
- Observation Sanitizer (Minimal Disclosure Layer)
- Compute Domain (AI)
- Proposal Buffer
- Ø Execution Gate
- Execution Domain
- Audit Layer

Legal influence path:

```
AI → Proposal Buffer → Ø Gate → Execution
```

All other direct paths to Execution are structurally forbidden.

---

## 5. Privilege Model

AI proposals operate under three privilege tiers:

- **P0** — No influence
- **P1** — Constrained assist (default)
- **P2** — Authorized assist (time-limited, bounded)

AI cannot self-escalate privilege. Escalation requires explicit human
authorization and TTL expiration.

---

## 6. Proposal Shaping

Before merging into execution, AI proposals undergo:

- Relative amplitude clamping
- Slew-rate limiting
- Rate limiting
- Quantization
- Privilege-based gain bounding

Final execution:

```
u_exec(t) = u_h(t) + α(p) * u_ai_shaped(t)
```

where `u_h` is human intent, `α(p) ≤ α_max < 1`, and `α(P0) = 0`.

---

## 7. State Machine

The Ø Gate operates in four states:

- NORMAL
- DEGRADED
- ISOLATED
- RECOVERY

Under uncertainty or integrity violation, the system fails closed by
reducing AI influence (authority decay), never by escalating it.

---

## 8. Scope

Spinal-Shield is architecture-level. It does not specify:

- Hardware implementation
- Specific sensor types
- Cryptographic primitives
- UI design

It specifies structural constraints that any compliant system must
enforce.

---

## 9. Repository Structure

- `README.md` (this file)
- `SPINAL_SHIELD_OVERVIEW.md`
- `GRAPH_SPEC_V0_1.md`
- `INTERFACE_CONTRACT_V0_1.md`
- `PRIVILEGE_POLICY_V0_1.md`
- `PROPOSAL_SHAPING_POLICY_V0_1.md`
- `O_GATE_STATE_MACHINE_V0_1.md` (Ø Gate State Machine)
- `PARAMS_V0_1.md`
- `AXIOM_TRACEABILITY_MATRIX_V0_1.md`
- `COMPLIANCE_TEST_V0_1.md`
- `SIMULATION_RESULTS_V0_3.md` (supersedes v0.2, which supersedes v0.1 — full revision history kept for transparency)

---

## 10. Status

**Version:** v1.0 (Reference Architecture Skeleton)
**Relationship:** Domain-specific instantiation of Asymmetric Authority
Architecture (DOI: 10.5281/zenodo.21384892)

This repository defines a structural baseline for execution-authority
enforcement in embodied AI. Future versions may extend formal proofs,
simulation results, and deployment patterns.
