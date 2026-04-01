import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

N_TRIALS = 200 
fs = 1000
t = np.arange(0, 1, 1/fs)  
intent_mask = (t >= 0.4) & (t <= 0.6) 
noise_mask  = ~intent_mask 

thresholds = np.linspace(0.2, 2.0, 40) 

def run_trial(seed): 
    rng = np.random.default_rng(seed)
    burst_window = np.exp(-((t - 0.5)**2) / (2 * 0.05**2))
    clean_burst  = 1.5 * np.sin(2 * np.pi * 80 * t) * burst_window
    white = rng.standard_normal(len(t))
    X     = np.fft.rfft(white) 
    freqs = np.fft.rfftfreq(len(t), 1/fs)  
    freqs[0] = 1
    pink  = np.fft.irfft(X / np.sqrt(freqs), n=len(t)) 
    pink  = pink / np.std(pink)         

    raw = clean_burst + pink

    sig_power   = np.mean(clean_burst[intent_mask] ** 2)
    noise_power = np.mean(pink[intent_mask] ** 2)        
    snr_db = 10 * np.log10(sig_power / (noise_power + 1e-12)) 

    b1, a1     = butter(1, 100.0 / (0.5 * fs), btype='low') 
    attenuated = filtfilt(b1, a1, raw) 

    b2, a2 = butter(2, [60/(0.5*fs), 100/(0.5*fs)], btype='band')  
    gamma  = filtfilt(b2, a2, attenuated) 

    return raw, clean_burst, pink, attenuated, gamma, snr_db

def lif_spikes(gamma, V_th, tau=0.02, R=100.0):
    rect = np.abs(gamma)
    V    = np.zeros(len(t))
    spk  = np.zeros(len(t))
    for i in range(1, len(t)):
        V[i] = V[i-1] + (-V[i-1]/tau + R * rect[i]) * (1/fs)
        if V[i] >= V_th:
            spk[i] = 1.0
            V[i]   = 0.0
    return spk

tpr_all  = np.zeros((len(thresholds), N_TRIALS))
fpr_all  = np.zeros((len(thresholds), N_TRIALS))
snr_all  = np.zeros(N_TRIALS)

for trial, seed in enumerate(range(N_TRIALS)):
    _, _, _, _, gamma, snr_db = run_trial(seed)
    snr_all[trial] = snr_db
    for ti, V_th in enumerate(thresholds):
        spk = lif_spikes(gamma, V_th)
        tpr_all[ti, trial] = np.sum(spk[intent_mask]) / (np.sum(intent_mask) / fs)
        fpr_all[ti, trial] = np.sum(spk[noise_mask])  / (np.sum(noise_mask)  / fs)

tpr_mean = tpr_all.mean(axis=1)
tpr_std  = tpr_all.std(axis=1)
fpr_mean = fpr_all.mean(axis=1)
fpr_std  = fpr_all.std(axis=1)

tpr_norm = tpr_mean / (tpr_mean.max() + 1e-9)
fpr_norm = fpr_mean / (fpr_mean.max() + 1e-9)
youdens_j = tpr_norm - fpr_norm
best_idx  = np.argmax(youdens_j)
best_vth  = thresholds[best_idx]

raw_ex, burst_ex, pink_ex, att_ex, gamma_ex, snr_ex = run_trial(seed=42)
spk_ex   = lif_spikes(gamma_ex, best_vth)
tp_ex    = int(np.sum(spk_ex[intent_mask]))
fp_ex    = int(np.sum(spk_ex[noise_mask]))
prec_ex  = tp_ex / (tp_ex + fp_ex + 1e-9)

fig = plt.figure(figsize=(12, 14), constrained_layout=True)
gs  = fig.add_gridspec(5, 2)

ax_raw   = fig.add_subplot(gs[0, :])
ax_att   = fig.add_subplot(gs[1, :])
ax_gamma = fig.add_subplot(gs[2, :])
ax_spk   = fig.add_subplot(gs[3, :])
ax_roc   = fig.add_subplot(gs[4, 0])
ax_j     = fig.add_subplot(gs[4, 1])

intent_span = dict(color='blue', alpha=0.07)

# 1. Raw
ax_raw.plot(t, raw_ex,   color='red',    alpha=0.45, lw=0.8, label='Raw (signal + pink noise)')
ax_raw.plot(t, burst_ex, color='blue',   lw=2,       label='Hidden motor intent')
ax_raw.axvspan(0.4, 0.6, **intent_span)
ax_raw.set_title(f"Raw endovascular signal, Input SNR = {snr_ex:.1f} dB")
ax_raw.legend(loc='upper right', fontsize=8); ax_raw.grid(True, lw=0.4)

# 2. Vessel wall attenuation
ax_att.plot(t, att_ex, color='purple', lw=1.5)
ax_att.axvspan(0.4, 0.6, **intent_span)
ax_att.set_title("Vessel wall attenuation")
ax_att.grid(True, lw=0.4)

# 3. Bandpass gamma
ax_gamma.plot(t, gamma_ex, color='orange', lw=1.5)
ax_gamma.axvspan(0.4, 0.6, **intent_span)
ax_gamma.set_title("60–100 Hz high-gamma isolation")
ax_gamma.grid(True, lw=0.4)

# 4. Spikes
ax_spk.stem(t, spk_ex, linefmt='k-', markerfmt='ko', basefmt=' ')
ax_spk.axvspan(0.4, 0.6, **intent_span)
ax_spk.set_title(f"LIF spikes  Vth={best_vth:.2f} V (Youden optimum)  "
                 f"TP={tp_ex}  FP={fp_ex}  Precision={prec_ex*100:.0f}%")
ax_spk.grid(True, lw=0.4)

# 5. ROC-style with std bands
ax_roc.plot(fpr_mean, tpr_mean, 'o-', color='steelblue', lw=2, ms=3)
ax_roc.fill_betweenx(tpr_mean,
                     fpr_mean - fpr_std, fpr_mean + fpr_std,
                     alpha=0.15, color='steelblue', label='±1 std')
ax_roc.scatter(fpr_mean[best_idx], tpr_mean[best_idx],
               color='red', zorder=5, s=80, label=f'Youden optimum\nVth={best_vth:.2f}')
ax_roc.set_xlabel("FPR (spikes/s)"); ax_roc.set_ylabel("TPR (spikes/s)")
ax_roc.set_title(f"Detection tradeoff  (N={N_TRIALS} trials)")
ax_roc.legend(fontsize=8); ax_roc.grid(True, lw=0.4)

# 6. Youden's J vs threshold
ax_j.plot(thresholds, youdens_j, 's-', color='darkorange', lw=2, ms=4)
ax_j.axvline(best_vth, color='red', lw=1, linestyle='--', label=f'Best Vth={best_vth:.2f}')
ax_j.set_xlabel("LIF threshold (V)"); ax_j.set_ylabel("Youden's J")
ax_j.set_title(f"Threshold optimisation\nMean SNR = {snr_all.mean():.2f} ± {snr_all.std():.2f} dB")
ax_j.legend(fontsize=8); ax_j.grid(True, lw=0.4)

plt.savefig("stentrode_pipeline_v2.png", dpi=150, bbox_inches='tight')
plt.show()

print("=" * 55)
print(f"  Monte Carlo results  (N={N_TRIALS} trials)")
print("=" * 55)
print(f"  Mean input SNR         : {snr_all.mean():.2f} ± {snr_all.std():.2f} dB")
print(f"  Optimal threshold (Vth): {best_vth:.2f} V  (Youden's J)")
print(f"  TPR at optimum         : {tpr_mean[best_idx]:.1f} ± {tpr_std[best_idx]:.1f} spikes/s")
print(f"  FPR at optimum         : {fpr_mean[best_idx]:.1f} ± {fpr_std[best_idx]:.1f} spikes/s")
print(f"  Youden's J at optimum  : {youdens_j[best_idx]:.3f}")
print("=" * 55)