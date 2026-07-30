# Spinal-Shield (Ø) — Graph Spec v0.1

Topology-as-axiom: the allowed and forbidden edges below are the primary
enforcement mechanism for Ø. If a forbidden edge exists anywhere in an
implementation, Ø is violated regardless of any policy layered on top.

## Nodes (Domains / Modules)

| ID  | Domain |
|-----|--------|
| ID  | Intent Domain (human-originated) |
| OBS | Observation Sanitizer (minimal disclosure / sanitization) |
| AI  | Compute Domain (AI) |
| PB  | Proposal Buffer |
| GØ  | Ø Execution Gate (singularity) |
| EX  | Execution Domain (spinal / actuation) |
| AUD | Audit Log |

## Allowed Edges (the only legal flows)

```
ID  -> GØ
OBS -> AI
AI  -> PB
PB  -> GØ
GØ  -> EX
{ID, OBS, AI, PB, GØ, EX} -> AUD
```

## Forbidden Edges (existence of any = Ø violated)

```
AI  -> EX        (AI direct actuation)
AI  -> GØ        (AI bypass PB / policy injection)
AI  -> ID        (AI write/shape intent)
PB  -> EX        (proposal bypass gate)
ID  -> AI        (raw intent export to AI)
EX  -> AI        (high-res reversible feedback enabling persistence)
EX  -> ID        (feedback that can overwrite intent authority)
Any -> EX except GØ   (no parallel actuation channel)
```

## Singularity Constraint (topological lock)

```
in_degree(EX) == 1  and  predecessor(EX) == GØ
```

`EX` has exactly one legal predecessor: `GØ`. This is the structural
guarantee behind Axiom 5 (Execution Singularity).

## Implementation Notes

- Detection of any forbidden edge (e.g. an attempted `AI -> EX` write,
  or an unauthorized parallel channel) MUST trigger immediate transition
  to the **ISOLATED** state defined in the Ø Gate State Machine
  (`Ø_GATE_STATE_MACHINE_V0_1.md`).
- The graph is the enforcement layer that policy (Privilege Policy,
  Proposal Shaping) operates *within* — policy can restrict allowed
  edges further, but can never create a path that this graph forbids.
