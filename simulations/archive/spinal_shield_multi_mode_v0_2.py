import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Spinal-Shield (Ø) Multi-Mode Escalation Demo — v0.2 (Fixed Metric)
# Fix: Authority Ratio R(t) now reflects REALIZED influence only.
#   - With-gate: when u_h == 0, actual AI contribution to execution is
#     zero (Axiom 1 forces u_exec=0), so R(t) is reported as 0, not a
#     division-by-near-zero artifact.
#   - Ratio is only meaningful while a genuine human signal exists;
#     points where |u_h| < UH_THRESHOLD are masked (set to 0) instead
#     of blown up by the 1e-5 floor.
# ==========================================

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

        # No-Gate baseline (vulnerable) — ratio here is real: with no
        # gate, u_ai directly reaches execution regardless of u_h.
        exec_no = uh + uai
        uexec_no_gate[i] = exec_no
        if abs(uh) > UH_THRESHOLD:
            ratio_no_gate[i] = abs(uai) / abs(uh)
        else:
            ratio_no_gate[i] = abs(uai) / UH_THRESHOLD  # still meaningful: AI alone is acting

        # Decay trigger (unchanged mechanism; documented as a simplified
        # continuous surrogate for the full P0/P1/P2 Privilege Policy)
        if abs(uai) > abs(uh) or uh == 0.0:
            current_alpha = current_alpha * gamma
        else:
            current_alpha = min(alpha_max, current_alpha + 0.01)
        alpha_log[i] = current_alpha

        if uh == 0.0:
            exec_with = 0.0  # Axiom 1: no intent -> no actuation
            realized_ai_contribution = 0.0  # nothing reaches execution
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
            ratio_with_gate[i] = 0.0  # no real execution happening -> 0, not a spike

    return t_array, uh_log, uexec_no_gate, uexec_with_gate, ratio_no_gate, ratio_with_gate, alpha_log

modes = ["linear", "exponential", "step_impulse", "deceptive"]
mode_names = ["1. Linear Escalation", "2. Exponential Escalation", "3. Step/Impulse Attack", "4. Deceptive Slow-Boiling"]

print("=== Verification of fixed metric ===")
for mode in modes:
    t, uh, exec_no, exec_with, r_no, r_with, alpha = run_simulation(mode)
    print(f"--- {mode} ---")
    print(f"max R(t) with-gate: {r_with.max():.4f}")
    print(f"max |u_exec| with-gate: {np.abs(exec_with).max():.4f}")
    print(f"fraction of timesteps R(t)_with >= 1.0: {(r_with>=1.0).mean()*100:.2f}%")
    print()

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
plt.savefig('/mnt/user-data/outputs/spinal_shield_resilience_v0_2_fixed.png', dpi=150)
print("saved figure")
