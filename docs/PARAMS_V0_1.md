# Spinal-Shield (Ø) — Parameter Registry v0.1

## 0. Purpose

Centralized registry of all tunable parameters. No parameter setting
may violate the Ø invariants below.

---

## 1. Global Invariants (non-negotiable, never runtime-modifiable)

```
α_max < 1
in_degree(EX) == 1
α(P0) = 0
no human intent => u_exec = 0
```

---

## 2. Influence Parameters

```
α_max = 0.49        # hard ceiling (<1 required)

# P1 (default assist)
α1 = 0.10
β1 = 0.20            # relative amplitude clamp
γ1 = 0.05            # slew-rate ratio

# P2 (authorized assist)
α2 = 0.25
β2 = 0.50
γ2 = 0.10
```

Constraints: `0 ≤ α1 ≤ α2 ≤ α_max`, `0 ≤ β1 ≤ β2 ≤ 1`, `0 ≤ γ1 ≤ γ2`

---

## 3. Quantization / Resolution

```
q1 = "coarse"        # P1
q2 = "medium"        # P2
```
Quantization must not enable covert high-resolution signaling.

---

## 4. Rate Limits

```
r1 = LOW_RATE
r2 = MEDIUM_RATE
```
`r1 ≤ r2`

---

## 5. Privilege Thresholds

```
L_hi = 0.80
L_lo = 0.50
```

---

## 6. TTL & Dwell Timers

```
TTL_P2 = 5s

N_L_RECOVER          = 20 cycles
M_ANOMALY_CLEAR       = 50 cycles
K0_RECOVERY_STAGE0    = 30 cycles
K1_RECOVERY_STAGE1    = 50 cycles
```

---

## 7. Degraded Mode Parameters

```
α_deg = 0.05
β_deg = 0.10
γ_deg = 0.03
```
Must satisfy: `α_deg ≤ α1`, `β_deg ≤ β1`, `γ_deg ≤ γ1`

---

## 8. Recovery Mode Parameters

```
α_r1 = 0.05
```
Must satisfy: `α_r1 ≤ α1`

---

## 9. Status

These are conservative starting defaults, not empirically validated
values. Tuning against a concrete system (e.g. the planned 2-link
planar arm simulation) is expected before any deployment claim.
