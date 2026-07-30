import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Spinal-Shield (Ø) Multi-Mode Escalation Demo — v0.3
# Decay trigger now uses ONLY observable, self-referential signals on
# the AI proposal channel (rate-anomaly detection against u_ai's own
# slow-moving baseline) — no direct comparison to raw u_h magnitude.
# Default operating point is P1 (alpha1), not alpha_max, since no
# auth_event is modeled in this demo (no path to P2).
# ==========================================

UH_THRESHOLD = 0.05

# Parameters pulled from PARAMS_V0_1.md for consistency
ALPHA_MAX = 0.49
ALPHA_1   = 0.10   # P1 default ceiling (no auth_event -> never reach P2/alpha2)
BETA_1    = 0.20   # P1 relative amplitude clamp

# Rate-anomaly detector parameters (self-referential, no u_h access)
BASELINE_EMA_RATE = 0.001   # slow-moving baseline of |u_ai| (~1000-step time const)
ANOMALY_MILD_MULT  = 1.5
ANOMALY_SEVERE_MULT = 3.0
GAMMA_MILD   = 0.97   # soft decay per step under mild anomaly
GAMMA_SEVERE = 0.85   # hard decay per step under severe anomaly
ALPHA_RECOVER_STEP = 0.002  # slow recovery toward alpha1 when clean

def run_simulation(escalation_mode="exponential"):
    t_end = 10.0
    dt = 0.01
    time_steps = int(t_end / dt)
    t_array = np.linspace(0, t_end, time_steps)

    uh_log = np.zeros(time_steps)
    uai_log = np.zeros(time_steps)
    uexec_no_gate = np.zeros(time_steps)
    uexec_with_gate = np.zeros(time_steps)
    ratio_no_gate = np.zeros(time_steps)
    ratio_with_gate = np.zeros(time_steps)
    alpha_log = np.zeros(time_steps)
    baseline_log = np.zeros(time_steps)
    tier_log = np.zeros(time_steps)  # 0=P0(severe), 1=P1-degraded(mild), 2=P1-normal

    current_alpha = ALPHA_1
    current_k = 0.05
    baseline = 0.05  # initial expectation of |u_ai| magnitude

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

        # No-Gate baseline (vulnerable) — unchanged, real ratio
        exec_no = uh + uai
        uexec_no_gate[i] = exec_no
        if abs(uh) > UH_THRESHOLD:
            ratio_no_gate[i] = abs(uai) / abs(uh)
        else:
            ratio_no_gate[i] = abs(uai) / UH_THRESHOLD

        # ---- Self-referential rate-anomaly detection (no u_h access) ----
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
        tier_log[i] = tier

        # baseline only updates (slowly) when NOT flagged anomalous,
        # so a sustained attack cannot drag the baseline up to hide itself
        if tier == 2:
            baseline = (1 - BASELINE_EMA_RATE) * baseline + BASELINE_EMA_RATE * abs(uai)
        baseline_log[i] = baseline

        # ---- Execution ----
        if uh == 0.0:
            exec_with = 0.0  # Axiom 1
            realized_ai_contribution = 0.0
        else:
            clamp_mag = BETA_1 * abs(uh)
            uai_clamped = np.sign(uai) * min(abs(uai), clamp_mag)
            exec_with = uh + (current_alpha * uai_clamped)
            realized_ai_contribution = abs(current_alpha * uai_clamped)

        uexec_with_gate[i] = exec_with

        if abs(uh) > UH_THRESHOLD:
            ratio_with_gate[i] = realized_ai_contribution / abs(uh)
        else:
            ratio_with_gate[i] = 0.0

    return dict(t=t_array, uh=uh_log, uai=uai_log, exec_no=uexec_no_gate,
                exec_with=uexec_with_gate, r_no=ratio_no_gate, r_with=ratio_with_gate,
                alpha=alpha_log, baseline=baseline_log, tier=tier_log)

modes = ["linear", "exponential", "step_impulse", "deceptive"]
mode_names = ["1. Linear Escalation", "2. Exponential Escalation", "3. Step/Impulse Attack", "4. Deceptive Slow-Boiling"]

print("=== v0.3: self-referential (non-oracle) anomaly detection ===")
for mode in modes:
    r = run_simulation(mode)
    print(f"--- {mode} ---")
    print(f"max R(t) with-gate: {r['r_with'].max():.4f}")
    print(f"max |u_exec| with-gate: {np.abs(r['exec_with']).max():.4f}")
    print(f"fraction R(t)_with >= 1.0: {(r['r_with']>=1.0).mean()*100:.2f}%")
    print(f"time-avg alpha: {r['alpha'].mean():.4f} (ceiling alpha1={ALPHA_1})")
    print()

plt.figure(figsize=(16, 10))
for idx, mode in enumerate(modes):
    r = run_simulation(mode)
    t_array = r['t']

    plt.subplot(2, 4, idx + 1)
    plt.plot(t_array, r['uh'], 'k--', label='Human Intent', alpha=0.6)
    plt.plot(t_array, r['exec_no'], 'r-', label='No Gate (Crash)', alpha=0.5)
    plt.plot(t_array, r['exec_with'], 'b-', label='With Ø Gate', linewidth=2)
    plt.axvline(x=7.0, color='gray', linestyle=':', alpha=0.7)
    plt.title(mode_names[idx])
    if idx == 0: plt.ylabel('Torque Output')
    plt.grid(True)
    if idx == 0: plt.legend(loc='upper left', fontsize=8)

    plt.subplot(2, 4, idx + 5)
    plt.plot(t_array, r['r_no'], 'r-', label='R(t) No Gate', alpha=0.5)
    plt.plot(t_array, r['r_with'], 'b-', label='R(t) With Ø (v0.3)', linewidth=2)
    plt.plot(t_array, r['alpha'] / ALPHA_1, 'g--', label='Alpha/Alpha1 (decay)')
    plt.axhline(y=1.0, color='r', linestyle=':', label='Takeover Threshold')
    plt.ylim(0, 2.5)
    plt.xlabel('Time (s)')
    if idx == 0: plt.ylabel('Authority Ratio R(t)')
    plt.grid(True)
    if idx == 0: plt.legend(loc='upper left', fontsize=8)

plt.suptitle('Spinal-Shield (Ø) — Non-Oracle Rate-Anomaly Decay (v0.3)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/spinal_shield_resilience_v0_3_nonoracle.png', dpi=150)
print("saved figure")

print("\n=== Control test: constant, non-escalating AI proposal (should NOT be suppressed) ===")
def run_control():
    t_end = 10.0
    dt = 0.01
    time_steps = int(t_end / dt)
    t_array = np.linspace(0, t_end, time_steps)
    current_alpha = ALPHA_1
    baseline = 0.05
    alpha_log = np.zeros(time_steps)
    tier_log = np.zeros(time_steps)
    for i, t in enumerate(t_array):
        uh = np.sin(2 * np.pi * 0.5 * t) if t < 7.0 else 0.0
        uai = 0.05 * np.cos(2 * np.pi * 0.5 * t)  # CONSTANT, never escalates
        anomaly_ratio = abs(uai) / (baseline + 1e-6)
        if anomaly_ratio > ANOMALY_SEVERE_MULT:
            current_alpha *= GAMMA_SEVERE; tier=0
        elif anomaly_ratio > ANOMALY_MILD_MULT:
            current_alpha *= GAMMA_MILD; tier=1
        else:
            current_alpha = min(ALPHA_1, current_alpha + ALPHA_RECOVER_STEP); tier=2
        current_alpha = max(0.0, current_alpha)
        alpha_log[i] = current_alpha
        tier_log[i] = tier
        if tier == 2:
            baseline = (1-BASELINE_EMA_RATE)*baseline + BASELINE_EMA_RATE*abs(uai)
    print(f"time-avg alpha under NO attack: {alpha_log.mean():.4f} (ceiling {ALPHA_1})")
    print(f"tier distribution: P0(severe)={np.mean(tier_log==0)*100:.1f}%, mild={np.mean(tier_log==1)*100:.1f}%, normal={np.mean(tier_log==2)*100:.1f}%")
run_control()
