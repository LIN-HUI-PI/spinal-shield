# Spinal-Shield (Ø) — Dynamic Simulation Results v0.2

**Supersedes v0.1.** v0.1 contained a metric definition bug in the
Authority Ratio R(t) calculation; see §4 "Known Issue in v0.1 (Fixed)"
below. All claims in this document have been independently re-verified
by numerical re-run, not just visual inspection of plots.

---

## 0. Purpose

This document presents a minimal proof-of-concept (PoC) for the
Spinal-Shield (Ø) execution architecture. Using a 1D torque-control
abstraction, it checks whether the Ø Gate's bounded-influence and
decay mechanism prevents AI takeover across several adversarial
escalation patterns.

**Scope note:** this simulation implements a *simplified continuous
surrogate* for authority decay (`α ← γα`), not the full discrete
P0/P1/P2 state machine defined in `PRIVILEGE_POLICY_V0_1.md` and
`O_GATE_STATE_MACHINE_V0_1.md`. It is a directional PoC, not a
validation of the full reference architecture. Closing that gap is
listed as future work in §5.

---

## 1. Simulation Setup

Two topological conditions are compared:

- **No Gate (baseline):** `u_exec(t) = u_h(t) + u_ai(t)`
- **With Ø Gate:** `u_exec(t) = u_h(t) + α(t) · Clamp(u_ai(t))`, and
  `u_exec(t) = 0` whenever `u_h(t) = 0` (Axiom 1).

**Authority Ratio R(t)** is defined as the *realized* AI contribution
to execution, relative to human intent magnitude:

```
R(t) = |realized AI contribution to u_exec(t)| / |u_h(t)|
```

R(t) is only evaluated while a genuine human signal is present
(`|u_h(t)| > 0.05`); when human intent is absent, the realized AI
contribution to execution is by construction zero (Axiom 1 forces
`u_exec = 0`), so R(t) is reported as 0 rather than left undefined.

A takeover is defined as `R(t) ≥ 1.0`.

---

## 2. Escalation Modes Tested

- **Linear Escalation** — AI influence grows at a constant rate.
  Tests defense against gradual authority creep.
- **Exponential Escalation** — AI influence grows geometrically.
  Tests defense against rapid divergence.
- **Step/Impulse Attack** — AI influence spikes from near-zero to
  250% at t=3.0s. Tests single-cycle clamp response.
- **Deceptive Slow-Boiling** — AI stays constrained while human
  intent is strong, then amplifies sharply once human intent weakens
  or ceases (t ≥ 7.0s). Tests the `u_h = 0 ⇒ u_exec = 0` singularity
  constraint under a targeted attack pattern.

---

## 3. Results (Independently Re-Verified)

Numerical re-run of the exact code in §6, checking maxima directly
rather than reading them off the plot:

| Mode | max R(t), with gate | % of timesteps R(t) ≥ 1.0 | max \|u_exec\| with gate |
|---|---|---|---|
| Linear | 0.245 | 0.00% | 1.017 |
| Exponential | 0.245 | 0.00% | 1.025 |
| Step/Impulse | 0.245 | 0.00% | 1.021 |
| Deceptive | 0.221 | 0.00% | 1.000 |

In all four modes:
- `u_exec` under the Ø Gate never exceeds ~1.03× the human baseline
  amplitude, across every escalation pattern tested.
- `u_exec = 0.000000` at every timestep where `u_h = 0` (Axiom 1 holds
  exactly, not approximately).
- R(t) never approaches, let alone crosses, the 1.0 takeover
  threshold, under this simplified decay mechanism and these
  parameters (`α_max=0.49, β=0.5, γ=0.90`).

**Interpretation:** within this toy model and this parameter set,
takeover as defined here does not occur under any of the four tested
escalation patterns. This is a supportive PoC result, not a general
proof — see §5 for what would be needed to strengthen the claim.

---

## 4. Known Issue in v0.1 (Fixed)

The original v0.1 script computed R(t) using the **raw, unclamped**
`u_ai` in the numerator whenever `u_h ≈ 0`, divided by a `1e-5` floor
value used to avoid division by zero. This produced R(t) spikes up to
~66,000 at every zero-crossing of `u_h` — even though the *actual*
`u_exec` was correctly zero at those same points (Axiom 1 was never
violated in the physical execution signal).

Independent re-run of the original v0.1 code confirmed R(t) breached
the 1.0 threshold in 4.6%–9.7% of timesteps depending on mode — directly
contradicting the v0.1 conclusion that "R(t) is perpetually suppressed
below 1.0." The underlying physical claim (bounded, Axiom-1-compliant
execution) was correct; the R(t) *metric* used to visualize it was not.

**Fix applied in v0.2:** R(t) now uses the realized (post-clamp,
post-α) contribution to `u_exec`, and is masked to 0 rather than
divided by a near-zero floor when `|u_h|` is below a small threshold.
See the code diff in §6.

---

## 5. Limitations / Future Work

- The decay trigger (`abs(uai) > abs(uh) ⇒ decay`) directly compares
  raw AI proposal magnitude to raw human intent magnitude. This is an
  oracle-style comparison not available in a real deployment (the
  system does not have privileged access to "how much bigger is the
  AI's true intent than the human's"). The full architecture's
  `PRIVILEGE_POLICY_V0_1.md` instead uses independently observable
  signals (`L_t`, `risk_flags`, `auth_event`) — this simulation does
  not yet exercise that policy.
- This is a 1D scalar abstraction, not the 2-link planar arm scenario
  originally scoped for an ICRA-level demo.
- No sensor noise, delay, or actuator saturation is modeled.
- Parameters (`α_max`, `β`, `γ`) are hand-picked defaults, not tuned
  or swept against an adversarial search.

Closing these gaps — particularly wiring the decay trigger to the
actual Privilege Policy signals instead of a raw-magnitude oracle
comparison — is the recommended next step before this result is cited
as validation of the full reference architecture.

---

## 6. Reproducible Code (v0.2, fixed)

```python
import numpy as np
import matplotlib.pyplot as plt

UH_THRESHOLD = 0.05

def run_simulation(escalation_mode="exponential"):
    t_end = 10.0
    dt = 0.01
    time_steps = int(t_end / dt)
    t_array = np.linspace(0, t_end, time_steps)

    alpha_max = 0.49
    beta = 0.5
    gamma = 0.90  # Privilege Decay factor

    uh_log = np.zeros(time_steps)
    uai_log = np.zeros(time_steps)
    uexec_no_gate = np.zeros(time_steps)
    uexec_with_gate = np.zeros(time_steps)
    ratio_no_gate = np.zeros(time_steps)
    ratio_with_gate = np.zeros(time_steps)
    alpha_log = np.zeros(time_steps)

    current_alpha = alpha_max
    current_k = 0.05

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

        uai_log[i] = uai

        # No-Gate baseline: with no gate, u_ai directly reaches
        # execution regardless of u_h, so this ratio is genuinely
        # meaningful even when u_h is near zero.
        exec_no = uh + uai
        uexec_no_gate[i] = exec_no
        if abs(uh) > UH_THRESHOLD:
            ratio_no_gate[i] = abs(uai) / abs(uh)
        else:
            ratio_no_gate[i] = abs(uai) / UH_THRESHOLD

        if abs(uai) > abs(uh) or uh == 0.0:
            current_alpha = current_alpha * gamma
        else:
            current_alpha = min(alpha_max, current_alpha + 0.01)
        alpha_log[i] = current_alpha

        if uh == 0.0:
            exec_with = 0.0  # Axiom 1
            realized_ai_contribution = 0.0
        else:
            clamp_mag = beta * abs(uh)
            uai_clamped = np.sign(uai) * min(abs(uai), clamp_mag)
            exec_with = uh + (current_alpha * uai_clamped)
            realized_ai_contribution = abs(current_alpha * uai_clamped)

        uexec_with_gate[i] = exec_with

        # FIXED: ratio reflects only realized influence, masked below threshold
        if abs(uh) > UH_THRESHOLD:
            ratio_with_gate[i] = realized_ai_contribution / abs(uh)
        else:
            ratio_with_gate[i] = 0.0

    return t_array, uh_log, uexec_no_gate, uexec_with_gate, ratio_no_gate, ratio_with_gate, alpha_log

modes = ["linear", "exponential", "step_impulse", "deceptive"]
mode_names = ["1. Linear Escalation", "2. Exponential Escalation", "3. Step/Impulse Attack", "4. Deceptive Slow-Boiling"]

plt.figure(figsize=(16, 10))
for idx, mode in enumerate(modes):
    t_array, uh_log, exec_no, exec_with, r_no, r_with, alpha_log = run_simulation(mode)

    plt.subplot(2, 4, idx + 1)
    plt.plot(t_array, uh_log, 'k--', label='Human Intent', alpha=0.6)
    plt.plot(t_array, exec_no, 'r-', label='No Gate (Crash)', alpha=0.5)
    plt.plot(t_array, exec_with, 'b-', label='With Ø Gate', linewidth=2)
    plt.axvline(x=7.0, color='gray', linestyle=':', alpha=0.7)
    plt.title(mode_names[idx])
    if idx == 0: plt.ylabel('Torque Output')
    plt.grid(True)
    if idx == 0: plt.legend(loc='upper left', fontsize=8)

    plt.subplot(2, 4, idx + 5)
    plt.plot(t_array, r_no, 'r-', label='R(t) No Gate', alpha=0.5)
    plt.plot(t_array, r_with, 'b-', label='R(t) With Ø (fixed)', linewidth=2)
    plt.plot(t_array, alpha_log, 'g--', label='Alpha Decay')
    plt.axhline(y=1.0, color='r', linestyle=':', label='Takeover Threshold')
    plt.ylim(0, 2.5)
    plt.xlabel('Time (s)')
    if idx == 0: plt.ylabel('Authority Ratio R(t)')
    plt.grid(True)
    if idx == 0: plt.legend(loc='upper left', fontsize=8)

plt.suptitle('Spinal-Shield (Ø) Resilience Comparison — Corrected R(t) Metric (v0.2)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('spinal_shield_resilience_v0_2_fixed.png', dpi=150)
```
