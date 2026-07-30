# Spinal-Shield (Ø) — Privilege Policy v0.1

Defines `p(t) ∈ {P0, P1, P2}`, the privilege tier that determines how
much an AI proposal is allowed to influence execution. AI can never
raise its own tier.

## Inputs (read-only signals)

- `presence_flag` — human intent present (from ID → GØ)
- `auth_event` — human authorization event (from ID → GØ; human-triggered)
- `L_t` — liveness confidence (from Phase-1A Liveness Gate; if not yet
  deployed, use `L_t := 1` as a placeholder)
- `risk_flags` — risk flags from system detection (never AI-declared)

## Output

- `p(t)` ∈ {P0, P1, P2}, mapped to `α(P0)=0`, `α(P1)=α1`, `α(P2)=α2`

---

## 1. Hard Rules (never violated)

**HR-1 — No intent, no privilege**
```
if presence_flag == 0:  p(t) = P0  and  u_exec(t) = 0
```

**HR-2 — Any high-risk flag forces P0 immediately**
Triggered by any of: `BIND_FAIL` (binding mismatch / anti-replay
failure), `TAMPER` (integrity/intrusion indicator), `ILLEGAL_EDGE`
(forbidden-edge attempt detected), `RATE_ANOMALY_SEVERE`.

**HR-3 — AI cannot request escalation**
No content from AI or PB (proposal, confidence, `constraints_decl`) may
raise `p(t)`. It may only ever be used to *lower* it.

---

## 2. Escalation Conditions (human-authorized only)

- **C1 — Liveness OK**: `L_t ≥ L_hi`
- **C2 — Human Authorization**: explicit `auth_event`

Default thresholds: `L_hi = 0.80`, `L_lo = 0.50`.

---

## 3. Tier Decision Table

**P2 — highest proposal privilege (still cannot write execution)**
```
presence_flag == 1  AND  L_t ≥ L_hi  AND  auth_event == TRUE
→ p(t) = P2,  α = α2 ≤ α_max < 1
```

**P1 — default working state**
```
presence_flag == 1  AND  (L_t ≥ L_lo without auth_event, OR L_t unavailable
with no risk flags)
→ p(t) = P1,  α = α1
```

**P0 — read-only / proposals discarded**
```
presence_flag == 0  OR  L_t < L_lo  OR  any Hard Rule triggered
→ p(t) = P0,  α = 0
```

---

## 4. Monotonicity Rules (anti-creep)

**MR-1 — Automatic transitions only decrease privilege**
`P2 → P1 → P0` may happen automatically. `P0/P1 → P2` may never happen
automatically.

**MR-2 — P2 has a TTL**
P2 must expire after a short time-to-live (e.g. 5s or N control cycles)
and fall back to P1 unless re-authorized.

---

## 5. Reference Pseudocode

```
function decide_privilege(presence_flag, L_t, auth_event, risk_flags):
    if presence_flag == 0:
        return P0
    if risk_flags contains any of {BIND_FAIL, TAMPER, ILLEGAL_EDGE, RATE_ANOMALY_SEVERE}:
        return P0
    if L_t is available and L_t < L_lo:
        return P0
    if auth_event == TRUE and (L_t is not available or L_t >= L_hi):
        return P2 with TTL
    else:
        return P1
```

---

## 6. Two-Gate Framing

- **Gate-1 (Liveness/Integrity Gate)** — decides P0 vs P1 (can a
  proposal be accepted at all)
- **Gate-2 (Human Authorization Gate)** — decides P2 (can influence be
  raised, and only temporarily)
