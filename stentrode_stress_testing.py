import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

N_TRIALS = 100
fs = 1000
t = np.arange(0, 1, 1/fs)
intent_mask = (t >= 0.4) & (t <= 0.6)
noise_mask = ~intent_mask
thresholds = np.linspace(0.3, 1.5, 30)

def run_stentrode_sim(cutoff, filter_order, label):
    tpr_list, fpr_list = [], []

    for seed in range(N_TRIALS):
        rng = np.random.default_rng(seed)

        burst = 1.5 * np.sin(2 * np.pi * 80 * t) * \
                np.exp(-((t - 0.5)**2) / (2 * 0.05**2))
        white = rng.standard_normal(len(t))
        X = np.fft.rfft(white)
        f_axis = np.fft.rfftfreq(len(t), 1/fs); f_axis[0] = 1
        pink = np.fft.irfft(X / np.sqrt(f_axis), n=len(t))
        pink = 1.0 * (pink / np.std(pink))   # consistent SNR across all runs

        raw = burst + pink

        # Vessel wall filter — order encodes number of capacitive layers
        b1, a1 = butter(filter_order, cutoff / (0.5 * fs), btype='low')
        attenuated = filtfilt(b1, a1, raw)

        b2, a2 = butter(2, [60/(0.5*fs), 100/(0.5*fs)], btype='band')
        gamma = filtfilt(b2, a2, attenuated)
        rect = np.abs(gamma)

        trial_tpr, trial_fpr = [], []
        for vth in thresholds:
            V = 0.0; spk = np.zeros(len(t))
            for i in range(1, len(t)):
                V += (-V/0.02 + 100.0 * rect[i]) * (1/fs)
                if V >= vth:
                    spk[i] = 1.0; V = 0.0

            # Normalised rates (0 to 1 scale) for proper ROC
            tpr_val = np.sum(spk[intent_mask]) / (np.sum(intent_mask) / fs)
            fpr_val = np.sum(spk[noise_mask])  / (np.sum(noise_mask)  / fs)
            trial_tpr.append(tpr_val)
            trial_fpr.append(fpr_val)

        tpr_list.append(trial_tpr)
        fpr_list.append(trial_fpr)

    tpr_mean = np.mean(tpr_list, axis=0)
    fpr_mean = np.mean(fpr_list, axis=0)

    # Youden's J optimum
    tpr_norm = tpr_mean / (tpr_mean.max() + 1e-9)
    fpr_norm = fpr_mean / (fpr_mean.max() + 1e-9)
    best_idx = np.argmax(tpr_norm - fpr_norm)

    print(f"\n{label}")
    print(f"  Optimal Vth : {thresholds[best_idx]:.2f} V")
    print(f"  TPR         : {tpr_mean[best_idx]:.1f} spikes/s")
    print(f"  FPR         : {fpr_mean[best_idx]:.1f} spikes/s")

    return tpr_mean, fpr_mean, best_idx

print("Testing Ideal Placement (100 Hz, 1st-order — single vessel wall layer)...")
tpr_100, fpr_100, best_100 = run_stentrode_sim(100.0, 1, "Ideal Placement")

print("Testing Poor Placement (50 Hz, 2nd-order — vessel wall + endothelial layer)...")
tpr_50,  fpr_50,  best_50  = run_stentrode_sim(50.0,  2, "Poor Placement")

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(fpr_100, tpr_100, 'g-o', ms=4, lw=2,
        label='Ideal placement — 100 Hz, order 1 (single RC layer)')
ax.plot(fpr_50,  tpr_50,  'r-o', ms=4, lw=2,
        label='Poor placement — 50 Hz, order 2 (vessel wall + endothelial layer)')

# Youden optima
ax.scatter(fpr_100[best_100], tpr_100[best_100],
           color='darkgreen', s=120, zorder=5,
           label=f"Ideal optimum  Vth={thresholds[best_100]:.2f} V")
ax.scatter(fpr_50[best_50],  tpr_50[best_50],
           color='darkred',   s=120, zorder=5,
           label=f"Poor optimum   Vth={thresholds[best_50]:.2f} V")

ax.set_title("Stress test: vessel wall thickness effect on decoding\n"
             "Order 1 = single capacitive layer  |  "
             "Order 2 = vessel wall + endothelial layer",
             fontsize=11)
ax.set_xlim([-1, 20])   # zoom into the clinically relevant region
ax.set_ylim([0, 120])   # cap at ~120 spikes/s max
ax.set_xlabel("False positive rate (spikes/s)")
ax.set_ylabel("True positive rate (spikes/s)")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
