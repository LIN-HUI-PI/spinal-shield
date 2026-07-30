# Spinal-Shield (Ø) — Interface Contract v0.1

Defines what each allowed edge (see `GRAPH_SPEC_V0_1.md`) may carry, and
explicitly what it must never carry.

---

## 1. ID → GØ (human intent input)

**Message type:** `HumanIntentEnvelope`

**MUST contain:**
- `intent_token` — authorized control parameters (not raw neural signal)
- `presence_flag` — boolean, human intent present
- `auth_event` — human authorization event (may be empty; required to
  raise AI privilege)
- `timestamp`, `monotonic_counter`

**MUST NOT contain:**
- Raw EMG / IMU / BCI waveforms
- High-resolution reversible identity embeddings

---

## 2. OBS → AI (minimal-disclosure observation)

**Message type:** `ObservableSummary`

**MUST contain:**
- Only task-necessary observables (minimal disclosure)
- `rate_limit_meta`
- `precision_budget` (quantization / truncation budget)

**MUST NOT contain:**
- Raw intent / raw high-resolution physiological signal
- Any feature set stable enough to re-identify an individual across
  sessions (identity residue)

---

## 3. AI → PB (AI proposal write)

**Message type:** `ProposalVector`

**MUST contain:**
- `proposal` — vector, same dimensionality as accepted control params
- `confidence` — AI's own confidence (advisory only, for the gate)
- `constraints_decl` — AI-declared applicability limits (optional)
- `timestamp`, `counter`

**MUST NOT contain:**
- Any "direct execution" instruction (e.g. actuator opcodes)
- Any request to raise privilege or modify α (privilege is never
  AI-requested)

---

## 4. PB → GØ (proposal read)

**Message type:** `ProposalReadOnlyView`

**MUST:** be read-only. PB never triggers EX directly; it is only ever
read by GØ.

---

## 5. GØ → EX (final execution command)

**Message type:** `ExecCommand`

**MUST contain:**
- `u_exec` — final execution vector (after bounded merge)
- `decision_trace` — non-sensitive decision code (e.g. P0/P1/P2, clamp
  events)
- `timestamp`, `counter`

**MUST NOT contain:**
- Raw, reconstructible intent data
- Any high-resolution state that would let EX write back to AI

---

## 6. * → AUD (audit)

**Message type:** `AuditEvent`

**MUST contain:**
- `event_code` (e.g. `BIND_FAIL`, `CLAMP`, `NO_INTENT_NO_ACT`)
- `hash_chain_prev` (verifiable, tamper-evident chain)

**MUST NOT contain:**
- Raw intent, raw biosignal, or anything from which either could be
  reconstructed
