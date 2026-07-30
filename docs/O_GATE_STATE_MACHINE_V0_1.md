# Spinal-Shield (Ø) — Gate State Machine v0.1

## 0. Purpose

Defines the time-evolution of the Ø Gate under normal operation,
degradation, isolation, and recovery. Goals:

- Enforce Ø invariants at all times
- Provide deterministic downgrade paths (authority decay)
- Prevent gradual authority creep
- Guarantee fail-closed behavior: when uncertain, reduce AI influence

Governs: privilege tier `p(t)`, AI influence `α(t)`, proposal shaping
constraints, and isolation behavior under suspicious access or
integrity failure.

---

## 1. States

- **S0 — NORMAL**: default. `p(t)` decided by Privilege Policy v0.1.
  P1 common; P2 only via explicit human authorization + TTL.
- **S1 — DEGRADED**: reduced AI influence and bandwidth. Triggered by
  low confidence (weak liveness, mild anomalies, partial sensor
  dropout). Keeps human execution stable while AI becomes less
  influential.
- **S2 — ISOLATED**: AI proposals fully disabled (`p(t)=P0`), or Compute
  Domain disconnected from proposal path. Triggered by
  integrity/tamper flags, replay/binding failures, forbidden-edge
  attempts, or severe exfiltration risk.
- **S3 — RECOVERY**: controlled re-entry after isolation. Gradually
  restores privileges with explicit checks to avoid abrupt
  re-enablement or attacker persistence.

---

## 2. Inputs (Events)

**Integrity / security:** `E_BIND_FAIL`, `E_TAMPER`, `E_ILLEGAL_EDGE`,
`E_RATE_ANOMALY_SEVERE`, `E_RATE_ANOMALY_MILD`

**Liveness / confidence:** `E_L_LOW`, `E_L_RECOVER`, `E_SENSOR_DROPOUT`,
`E_SENSOR_RECOVER`

**Human authorization:** `E_AUTH`, `E_AUTH_REVOKE`, `E_P2_TTL_EXPIRE`

**Operational:** `E_TIMEOUT`, `E_RESET`

---

## 3. Mandatory Invariants (always enforced)

- `presence_flag == 0` ⇒ `u_exec = 0` and `p(t) = P0`
- `α(t) ≤ α_max < 1` at all times
- Only `GØ` may write to `EX` (no parallel actuation channel)

---

## 4. Transition Rules

### 4.1 Any state → ISOLATED (S2) — hard triggers
On any of `E_TAMPER`, `E_BIND_FAIL`, `E_ILLEGAL_EDGE`,
`E_RATE_ANOMALY_SEVERE`:
```
s(t+) = S2,  p(t+) = P0,  α(t+) = 0
disable PB → GØ influence
optionally disable OBS → AI (minimal disclosure only)
emit ISOLATION_TRIGGERED + reason codes
```
This is fail-closed.

### 4.2 NORMAL (S0) → DEGRADED (S1) — soft triggers
On any of `E_L_LOW`, `E_SENSOR_DROPOUT`, `E_RATE_ANOMALY_MILD`:
```
s(t+) = S1
force p(t) ≤ P1 (P2 disallowed)
α ceiling reduced: α ≤ α_deg ≤ α1
tighten shaping (β_deg ≤ β1, γ_deg ≤ γ1, lower rate, coarser quantization)
emit DEGRADED_ENTERED + reason codes
```

### 4.3 DEGRADED (S1) → NORMAL (S0)
Requires all of: `E_L_RECOVER` sustained for N cycles, `E_SENSOR_RECOVER`,
no anomalies for M cycles. Then restore normal privilege policy and
shaping parameters; emit `DEGRADED_EXITED`.

### 4.4 ISOLATED (S2) → RECOVERY (S3)
Requires explicit human acknowledgment (`E_AUTH`) or session restart
(`E_RESET`), AND integrity conditions cleared (no tamper flag active).
`p(t) = P0` initially; enable only minimal safe interfaces; emit
`RECOVERY_ENTERED`. If `E_TAMPER` persists, remain in S2.

### 4.5 RECOVERY (S3) — staged re-enable
- **R0**: `p=P0, α=0`, proposals ignored; dwell K0 cycles with stable
  signals
- **R1** (if stable): P1 only, stricter `α ≤ α_r1 < α1`; dwell K1 cycles
- **Exit to NORMAL** if stable with no anomalies
- Any anomaly during RECOVERY → return to S2 immediately

---

## 5. Authority Decay Rules

**D1 — automatic decay**: increased uncertainty (lower `L_t`, rising
anomalies) forces `P2 → P1 → P0` and `α2 → α1 → 0` without requiring any
AI input.

**D2 — no automatic escalation**: privilege escalation requires an
explicit `E_AUTH` event, only from S0, and applies a P2 TTL. This
enforces Authority Monotonicity — automatic transitions only ever
decrease influence.

---

## 6. Edge Enablement by State

| Edge | S0 NORMAL | S1 DEGRADED | S2 ISOLATED | S3 RECOVERY |
|---|---|---|---|---|
| ID→GØ | enabled | enabled | enabled | enabled |
| OBS→AI | enabled | enabled | reduced/disabled | disabled → staged |
| AI→PB | enabled | enabled | disabled | disabled → staged (P1 only in R1) |
| PB→GØ | enabled | enabled (P2 off) | disabled (α=0) | disabled → staged |
| GØ→EX | enabled | enabled | enabled (human-only) | enabled |
| *→AUD | enabled | enabled (verbose) | enabled | enabled |

---

## 7. Minimum Audit Events

`STATE_ENTERED`, `STATE_EXITED`, `ISOLATION_TRIGGERED(reason)`,
`DECAY_APPLIED`, `P2_GRANTED(TTL)`, `P2_TTL_EXPIRED`,
`ILLEGAL_EDGE_DETECTED`, `BIND_FAIL` / `TAMPER` / `RATE_ANOMALY` flags.

No raw intent or raw physiology is ever stored in audit logs.

---

## 8. Notes

Parameter selection (`N`, `M`, `K0`, `K1`, `α_deg`, `α_r1`, etc.) is
implementation-tunable — see `PARAMS_V0_1.md`. The invariant structure
(fail-closed, monotonic decay, no AI-driven escalation) is not tunable.
