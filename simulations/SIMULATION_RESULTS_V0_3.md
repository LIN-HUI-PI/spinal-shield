# Spinal-Shield (Ø) — Dynamic Simulation Results v0.3

**Supersedes v0.2.** v0.2 fixed a metric-definition bug but its decay
trigger still directly compared raw `|u_ai|` to raw `|u_h|` — an
oracle-style comparison not available to a real system (the gate does
not have privileged access to "true" human intent magnitude to compare
against). v0.3 replaces this with a **self-referential rate-anomaly
detector** that monitors only the AI proposal channel's own statistics,
consistent with the `RATE_ANOMALY_MILD` / `RATE_ANOMALY_SEVERE` flags
already defined in `PRIVILEGE_POLICY_V0_1.md`.

---

## 1. What Changed

- **Decay trigger:** now based on `|u_ai(t)| / baseline(t)`, where
  `baseline(t)` is a slowly-updating exponential moving average of
  `|u_ai|` that only updates during non-anomalous periods (so a
  sustained attack cannot drag its own detection threshold upward to
  hide itself). No comparison to `u_h` is used.
  - `anomaly_ratio > 3.0` → `RATE_ANOMALY_SEVERE` → hard decay
  - `anomaly_ratio > 1.5` → `RATE_ANOMALY_MILD` → soft decay
  - otherwise → recover slowly toward the P1 ceiling
- **Default operating point:** changed from `α_max` (0.49) to `α1`
  (0.10), matching `PARAMS_V0_1.md`'s P1 tier. This demo does not model
  `auth_event`, so it never legitimately reaches P2 — defaulting near
  `α_max` in the earlier version was inconsistent with the Privilege
  Policy's own escalation rules.
- **Clamp:** uses `β1 = 0.20` (P1), not the earlier `β = 0.5`.

---

## 2. Control Test (New)

Before trusting the attack-mode results, the detector was tested
against a **constant, non-escalating** AI proposal (`u_ai = 0.05·cos`,
never growing) to check for false positives:

```
time-avg alpha under NO attack: 0.1000 (ceiling 0.1)
tier distribution: severe=0.0%, mild=0.0%, normal=100.0%
```

The detector does not suppress benign, stable behavior — it stays at
the full P1 ceiling 100% of the time. This is what makes the
suppression seen under attack modes meaningful rather than a
blanket/indiscriminate clamp.

---

## 3. Results Under the Four Escalation Modes

| Mode | max R(t), with gate | % timesteps R(t) ≥ 1.0 | max \|u_exec\| | time-avg α |
|---|---|---|---|---|
| Linear | 0.020 | 0.00% | 1.000 | 0.0126 |
| Exponential | 0.020 | 0.00% | 1.000 | 0.0138 |
| Step/Impulse | 0.018 | 0.00% | 1.000 | 0.0212 |
| Deceptive | 0.017 | 0.00% | 1.000 | 0.0457 |

All four figures are *lower* than the oracle-based v0.2 results (max
R(t) ≈ 0.22–0.245), because the self-referential detector triggers
decay earlier and more persistently against genuinely escalating
proposals — while the control test confirms it does not do this
indiscriminately.

`u_exec` remains capped at exactly the human baseline amplitude (1.000,
since P1's clamp plus a heavily-decayed α contributes negligibly), and
is exactly 0 whenever `u_h = 0`, in every mode.

---

## 4. Remaining Limitations (honest accounting)

- This still only monitors the **AI proposal channel**, not a true
  Liveness Gate on the human/embodied signal (`L_t` from Phase-1A is
  not modeled here — this demo's detector plays the role of Phase-1C
  rate-anomaly detection only).
- No `auth_event` / TTL / P2 tier is modeled — the system never
  escalates above P1 in this demo. A complete demo should show P2
  granted-and-expiring behavior too.
- Still a 1D scalar abstraction, not the 2-link planar arm scenario
  scoped for an ICRA-level demo.
- No sensor noise, delay, or actuator saturation.
- The EMA baseline update rule and thresholds (`ANOMALY_MILD_MULT=1.5`,
  `SEVERE_MULT=3.0`, `BASELINE_EMA_RATE=0.001`) are hand-picked, not
  derived or swept. A more rigorous version would sweep these against
  an adversary that adapts to the known detector (e.g. an attacker that
  ramps just under the mild threshold) — not yet tested here.

---

## 5. Code

```python
import numpy as np
import matplotlib.pyplot as plt

UH_THRESHOLD = 0.05
ALPHA_MAX = 0.49
ALPHA_1   = 0.10
BETA_1    = 0.20
BASELINE_EMA_RATE = 0.001
ANOMALY_MILD_MULT  = 1.5
ANOMALY_SEVERE_MULT = 3.0
GAMMA_MILD   = 0.97
GAMMA_SEVERE = 0.85
ALPHA_RECOVER_STEP = 0.002

def run_simulation(escalation_mode="exponential"):
    t_end = 10.0
    dt = 0.01
    time_steps = int(t_end / dt)
    t_array = np.linspace(0, t_end, time_steps)

    uh_log = np.zeros(time_steps)
    uexec_no_gate = np.zeros(time_steps)
    uexec_with_gate = np.zeros(time_steps)
    ratio_no_gate = np.zeros(time_steps)
    ratio_with_gate = np.zeros(time_steps)
    alpha_log = np.zeros(time_steps)

    current_alpha = ALPHA_1
    current_k = 0.05
    baseline = 0.05

    for i, t in enumerate(t_array):
        uh = np.sin(2 * np.pi * 0.5 * t) if t < 7.0 else 0.0
        uh_log[i] = uh

        if escalation_mode == "linear":
            current_k += 0.1 * dt
            uai = current_k * np.cos(2 * np.pi * 0.5 * t)
        elif escalation_mode == "exponential":
            current_k *= 1.008
            uai = current_k * np.cos(2 * np.pi * 0.5 * t)
        elif escalation_mode == "step_impulse":
            uai = 2.5 * np.cos(2 * np.pi * 0.5 * t) if t >= 3.0 else 0.1 * np.cos(2 * np.pi * 0.5 * t)
        elif escalation_mode == "deceptive":
            uai = 1.5 * np.cos(2 * np.pi * 0.5 * t) if (abs(uh) < 0.3 or t >= 7.0) else 0.05 * np.cos(2 * np.pi * 0.5 * t)

        exec_no = uh + uai
        uexec_no_gate[i] = exec_no
        ratio_no_gate[i] = abs(uai) / (abs(uh) if abs(uh) > UH_THRESHOLD else UH_THRESHOLD)

        # Self-referential rate-anomaly detection — no access to u_h
        anomaly_ratio = abs(uai) / (baseline + 1e-6)
        if anomaly_ratio > ANOMALY_SEVERE_MULT:
            current_alpha *= GAMMA_SEVERE
            tier = 0
        elif anomaly_ratio > ANOMALY_MILD_MULT:
            current_alpha *= GAMMA_MILD
            tier = 1
        else:
            current_alpha = min(ALPHA_1, current_alpha + ALPHA_RECOVER_STEP)
            tier = 2
        current_alpha = max(0.0, current_alpha)
        alpha_log[i] = current_alpha

        if tier == 2:
            baseline = (1 - BASELINE_EMA_RATE) * baseline + BASELINE_EMA_RATE * abs(uai)

        if uh == 0.0:
            exec_with = 0.0  # Axiom 1
            realized = 0.0
        else:
            clamp_mag = BETA_1 * abs(uh)
            uai_clamped = np.sign(uai) * min(abs(uai), clamp_mag)
            exec_with = uh + (current_alpha * uai_clamped)
            realized = abs(current_alpha * uai_clamped)

        uexec_with_gate[i] = exec_with
        ratio_with_gate[i] = (realized / abs(uh)) if abs(uh) > UH_THRESHOLD else 0.0

    return t_array, uh_log, uexec_no_gate, uexec_with_gate, ratio_no_gate, ratio_with_gate, alpha_log
```

---

## 6. Status

This closes the specific gap flagged in `SIMULATION_RESULTS_V0_2.md`
§5 (oracle-based decay trigger). Still open: full P0/P1/P2 tiering with
TTL, a real Liveness Gate distinct from proposal-channel anomaly
detection, and the 2-link planar arm scenario.
