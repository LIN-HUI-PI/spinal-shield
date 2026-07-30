# Spinal-Shield (Ø) — Graph Spec v1.1

> **v1.1 changes:** Added `RFX` (Reflex Pathway) and `PROX` (Bystander
> Proximity/Force Sensing) nodes. `RFX` sits entirely outside the Ø
> Gate's governance — see the note under Singularity Constraint below
> for how this coexists with Axiom 5 without contradiction.

Topology-as-axiom: the allowed and forbidden edges below are the primary
enforcement mechanism for Ø. If a forbidden edge exists anywhere in an
implementation, Ø is violated regardless of any policy layered on top.

## Nodes (Domains / Modules)

| ID   | Domain |
|------|--------|
| ID   | Intent Domain (human-originated) |
| OBS  | Observation Sanitizer (minimal disclosure / sanitization) |
| AI   | Compute Domain (AI) |
| PB   | Proposal Buffer |
| GØ   | Ø Execution Gate (singularity, governs AI-mediated actuation) |
| EX   | Execution Domain (spinal / actuation, AI-governable portion) |
| RFX  | Reflex Pathway (hardwired, physiological — see Axiom 0) |
| PROX | Bystander Proximity/Force Sensor (feeds a hard limiter, not a proposal — see Axiom I5) |
| AUD  | Audit Log |

## Allowed Edges (the only legal flows)

```
ID   -> GØ
OBS  -> AI
AI   -> PB
PB   -> GØ
GØ   -> EX
RFX  -> Actuator (hardwired, bypasses EX and GØ entirely — see Axiom 0)
PROX -> EX        (hard limiter input only, not a proposal — see below)
{ID, OBS, AI, PB, GØ, EX, RFX, PROX} -> AUD
```

## Forbidden Edges (existence of any = Ø violated)

```
AI   -> EX        (AI direct actuation)
AI   -> GØ        (AI bypass PB / policy injection)
AI   -> ID        (AI write/shape intent)
PB   -> EX        (proposal bypass gate)
ID   -> AI        (raw intent export to AI)
EX   -> AI        (high-res reversible feedback enabling persistence)
EX   -> ID        (feedback that can overwrite intent authority)
Any  -> EX except {GØ, PROX}   (no parallel AI-mediated actuation channel)
AI   -> RFX       (AI cannot touch the reflex pathway at all — Axiom 0)
GØ   -> RFX       (not even the Gate mediates reflex — Axiom 0)
PB   -> RFX
AI   -> PROX      (AI cannot influence the bystander safety limiter)
PROX -> AI        (no feedback path from the safety limiter to AI, to
                    prevent the limiter's threshold from becoming an
                    optimizable/gameable signal)
```

## Singularity Constraint (topological lock)

```
in_degree(EX) == 2   (predecessors: GØ and PROX only)
predecessor(EX) always includes GØ; PROX is a hard limiter, not an
  alternative actuation source — it can only clamp/veto GØ's output,
  never independently originate a command.
```

`EX` accepts commands only from `GØ`; `PROX` is not a second command
source but a limiter wired to clamp whatever `GØ` outputs. This is the
structural guarantee behind Axiom 5 (Execution Singularity) — Axiom 5
governs the single *AI-mediated command path*, not the reflex arc.

**Why `RFX` does not violate Axiom 5:** `RFX` never touches `EX` — it
connects directly to the physical actuator hardware, below and outside
the layer that Axiom 5 governs. Axiom 5's guarantee ("AI cannot find a
second path to command execution") and Axiom 0's guarantee ("reflexes
are never gated by anything AI-adjacent") are about different layers of
the system and do not conflict. If a future implementation cannot
physically separate `RFX` from `EX` (e.g. shared actuator hardware with
no independent low-level cutoff), that implementation does not satisfy
Axiom 0 and must not claim Spinal-Shield compliance until it can.

## Implementation Notes

- Detection of any forbidden edge (e.g. an attempted `AI -> EX` write,
  or an unauthorized parallel channel) MUST trigger immediate transition
  to the **ISOLATED** state defined in the Ø Gate State Machine
  (`Ø_GATE_STATE_MACHINE_V0_1.md`).
- The graph is the enforcement layer that policy (Privilege Policy,
  Proposal Shaping) operates *within* — policy can restrict allowed
  edges further, but can never create a path that this graph forbids.
- `RFX` (Axiom 0) is intentionally unmodeled by any policy layer in this
  spec — it is out of scope for Privilege Policy, Proposal Shaping, and
  the State Machine entirely, by design. Any document in this repo that
  appears to place `RFX` under gate/state-machine control is in error.
- `PROX` (I5, bystander safety) differs from `RFX` in kind: it is not a
  reflex of the *user's* body, but an environmental safety limiter. It
  IS allowed to clamp `EX`'s output (hence the edge `PROX -> EX`), but
  it cannot originate commands and AI cannot read or influence its
  threshold (see forbidden edges above).
