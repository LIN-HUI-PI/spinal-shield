# Spinal-Shield (Ø) — Proposal Shaping Policy v0.1

## 0. Purpose

Defines how AI proposals (`u_ai`) are transformed into a bounded
contribution before they are allowed to influence execution through the
Ø Gate: rate limiting, amplitude limiting, resolution limiting,
slew-rate limiting, and a safety clamp relative to human intent
magnitude.

Key principle: AI proposals are never executed directly. Influence is
always bounded and privilege-gated by `p(t)`. When in doubt, degrade
privilege and reduce AI influence.

---

## 1. Inputs / Outputs

**Inputs:**
- `u_h(t)` — authorized human control parameters
- `u_ai(t)` — AI proposal vector
- `p(t)` — privilege tier {P0, P1, P2}
- `dt` — control step interval

**Output:**
- `ũ_ai(t)` — shaped proposal vector used in bounded merge

---

## 2. Shaping Operators (abstract composition)

```
ũ_ai(t) = Q_p( S_p( R_p( C_p(u_ai(t), u_h(t)) ) ) )
```

- `C_p` — clamp (relative amplitude bound to `u_h`)
- `R_p` — rate limit (bandwidth / message rate)
- `S_p` — slew-rate limit (max change per step)
- `Q_p` — quantize (resolution reduction)

Each operator depends on the privilege tier `p`.

---

## 3. Tier Definitions

### P0 — no proposal influence
```
α(P0) = 0
ũ_ai(t) := 0
u_exec(t) = u_h(t)   (or 0 if presence_flag = 0)
```

### P1 — constrained assist (default)
- Relative amplitude clamp: `‖u_ai‖ ≤ β1 ‖u_h‖`
- Slew-rate clamp: `‖Δu_ai‖ ≤ γ1 ‖u_h‖`
- Quantization: `q1` (coarser)
- Update rate limit: `r1` (lower)

AI may suggest small, smooth, coarse adjustments — preventing sudden
domination or oscillatory takeover.

### P2 — high-privilege proposals (still bounded)
- Relative amplitude clamp: `‖u_ai‖ ≤ β2 ‖u_h‖`
- Slew-rate clamp: `‖Δu_ai‖ ≤ γ2 ‖u_h‖`
- Quantization: `q2` (finer than P1)
- Update rate limit: `r2` (higher than P1)
- Must satisfy `β2 ≤ 1` and `α(P2) ≤ α_max < 1`

---

## 4. Operator Definitions

**C_p — relative amplitude clamp**
```
M_h = ‖u_h(t)‖,  M_ai = ‖u_ai(t)‖
if M_h = 0: return 0          # no human intent => no AI influence
else: C_p(u_ai, u_h) = u_ai * min(1, (β_p * M_h) / M_ai)
```

**R_p — rate limit**
Enforces maximum accepted proposal updates per second. If proposals
arrive faster than `r_p`, drop excess or keep latest only (pick one
policy, apply consistently). Rate limiting must never let AI bypass
P0/P1/P2 decisions.

**S_p — slew-rate limit**
```
Δu = u_ai(t) - u_ai(t - dt)
bound: ‖Δu‖ ≤ γ_p * ‖u_h(t)‖   (clamp if violated)
```

**Q_p — quantization**
P1 uses coarser quantization than P2. Reduces covert-channel capacity
and sensitivity to AI micro-perturbations; improves stability.

---

## 5. Integration with Ø Gate (bounded merge)

```
u_exec(t) = 0                              if presence_flag == 0
u_exec(t) = u_h(t) + α(p) * ũ_ai(t)        otherwise
```
with `α(P0) = 0`.

---

## 6. Audit Events (minimum set)

- `CLAMP_AMP_P1` / `CLAMP_AMP_P2`
- `CLAMP_SLEW_P1` / `CLAMP_SLEW_P2`
- `DROP_RATE_P1` / `DROP_RATE_P2`
- `QUANT_APPLIED_P1` / `QUANT_APPLIED_P2`
- `P_TIER_CHANGE`
- `P2_TTL_EXPIRED`

Audit logs record only event codes, tier, magnitude ratios (e.g.
`M_ai / M_h`), and timestamps/counters — never raw `u_h` or raw
physiology.

---

## 7. Conservative Default Parameters (starting point, to be tuned)

- `α_max = 0.49` (always < 0.5 — AI can never become dominant)
- P1: `α1 = 0.10, β1 = 0.20, γ1 = 0.05`
- P2: `α2 = 0.25, β2 = 0.50, γ2 = 0.10`
- `TTL_P2 = 5s`
- Rate: `r1 < r2`
- Quantization: P1 one level coarser than P2
