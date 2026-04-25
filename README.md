# Neuromorphic-Decoding-of-Attenuated-Endovascular-Signals

# Overview

This repository contains a systems level Python simulation of an event driven neuromorphic pipeline designed for endovascular Brain-Computer Interfaces (BCIs).

Minimally invasive BCIs (like the Stentrode) offer exceptional safety profiles but suffer from severe high-frequency signal attenuation due to the capacitive filtering of the blood vessel wall. Furthermore, standard digital decoding (e.g., on-sensor DSPs or FPGAs) is often too power hungry for micro implants operating within strict thermal limits.

This project is a discrete time computational feasibility study of a continuous time analog neuromorphic pipeline. It models biological tissue attenuation using a single pole RC low-pass filter whose cutoff frequency is grounded in the Randles cell corner frequency of the tissue-electrode interface. Spike encoding is modeled using a Leaky Integrate-and-Fire (LIF) neuron whose leak time constant mathematically corresponds to the engineered thermal time constant (R_th*C_th) of a VO₂ Mott insulator undergoing Joule heating — a volatile memristive device that, in physical hardware, would act as a threshold gatekeeper without the 60 mV/decade sub-threshold slope constraint of standard CMOS. This hardware advantage is the motivation for the VO₂-based encoding stage and is not directly validated by this simulation.


# System Architecture

The pipeline consists of five stages:

1. Signal & Noise Synthesis
Generates an 80 Hz high gamma motor intent burst (Gaussian-windowed sinusoid, σ = 0.05 s, centered at t = 0.5 s) buried in physiological 1/f pink noise. Input SNR is computed on the raw signal prior to any filtering, ensuring it reflects true pre processing conditions.

2. Biological Interface — Tissue Attenuation
Models the blood vessel wall as a 1st-order Butterworth low-pass filter (100 Hz cutoff), representing a single capacitive RC layer. The cutoff is physically grounded in the Randles equivalent circuit corner frequency of the endovascular electrode-tissue interface. In the stress test, poor electrode placement is modeled as a 2nd-order Butterworth (50 Hz cutoff), approximating two RC stages in series (vessel wall + endothelial layer).

3. Analog Front-End (AFE)
A 2nd-order Butterworth bandpass filter (60–100 Hz) isolates the high gamma band where motor intent encoding is strongest. Applied via zero phase filtfilt to avoid group delay artifacts.

5. Hardware Spike Encoder — VO₂ LIF Neuron
An event-driven Leaky Integrate-and-Fire neuron encodes gamma band activity into spike trains. The membrane potential evolves as:

V[i] = V[i−1] + (−V[i−1]/τ + R · |γ[i]|) · dt

with τ = 20 ms and R = 100 Ω. The leak term (−V/τ) is physically motivated by the thermal relaxation dynamics of a VO₂ Mott insulator, making the neuron's time constant directly mappable to a physical device parameter. When V ≥ V_th, a spike is emitted and V resets to zero.

5. Statistical Evaluation & Threshold Optimization
A Monte Carlo simulation sweeps voltage thresholds across multiple noise realizations. Youden's J statistic is computed on normalized spike rates (J = TPR_norm − FPR_norm) to account for the spike rate ROC space, where raw TPR and FPR values are in spikes/s rather than classical [0, 1] probabilities.

# Repository Contents

1. stentrode_pipeline.py

Performs a rigorous statistical evaluation of the baseline neuromorphic pipeline.

Method: 200-trial Monte Carlo simulation across randomly generated 1/f noise profiles

Optimization: Sweeps 40 hardware voltage thresholds V_th (0.2 V to 2.0 V)

Metric: Maximizes Youden's J statistic (computed on normalized spike rates) on the spike-rate ROC curve to identify the optimal firing threshold

Output: Composite figure showing time domain signal evolution through all pipeline stages, the spike rate ROC detection tradeoff with ±1 standard deviation bands, and the Youden's J optimization landscape

<img width="1918" height="972" alt="image" src="https://github.com/user-attachments/assets/6783119a-e0ed-4b19-bc04-64adbaec8427" />


2. stentrode_stress_testing.py

Stress-tests the pipeline architecture against varying degrees of electrode placement quality.

Ideal Placement: Modeled as a single vessel wall capacitive layer — 1st-order Butterworth low pass, 100 Hz cutoff

Poor Placement: Modeled as vessel wall plus endothelial layer (e.g., thick-walled vein or fibrotic encapsulation) — 2nd-order Butterworth low pass approximating two RC stages in series, 50 Hz cutoff. Pink noise amplitude is held constant across both conditions (σ = 1.0) so that attenuation model is the sole independent variable

Output: Comparative spike rate ROC curve demonstrating the severe vulnerability of high gamma signals to multi layer tissue impedance. Results suggest that static threshold calibration may be insufficient in vivo, and that electrode placement functions as a near binary viability threshold rather than a soft performance parameter

<img width="1918" height="922" alt="image" src="https://github.com/user-attachments/assets/b6dc4b89-7d23-458d-9df9-66e3139e77f4" />

# References

1. Electrode–Tissue Interface (Randles model foundation)

Merrill DR, Bikson M, Jefferys JG. Electrical stimulation of excitable tissue: design of efficacious and safe protocols. J Neurosci Methods. 2005 Feb 15;141(2):171-98. doi: 10.1016/j.jneumeth.2004.10.020.

2. Device Physics (VO₂ Memristor System)

Yuan R, Tiw PJ, Cai L, Yang Z, Liu C, Zhang T, Ge C, Huang R, Yang Y. A neuromorphic physiological signal processing system based on VO2 memristor for next-generation human-machine interface. Nat Commun. 2023 Jun 21;14(1):3695. doi: 10.1038/s41467-023-39430-4.

3. Neuromorphic Architecture (HFO Detection)

Sharifshazileh M, Burelo K, Sarnthein J, Indiveri G. An electronic neuromorphic system for real-time detection of high frequency oscillations (HFO) in intracranial EEG. Nat Commun. 2021 May 25;12(1):3095. doi: 10.1038/s41467-021-23342-2.

4. Endovascular BCI (Stentrode)

Oxley TJ, Opie NL, John SE, Rind GS, Ronayne SM, Wheeler TL, Judy JW, McDonald AJ, Dornom A, Lovell TJ, Steward C, Garrett DJ, Moffat BA, Lui EH, Yassi N, Campbell BC, Wong YT, Fox KE, Nurse ES, Bennett IE, Bauquier SH, Liyanage KA, van der Nagel NR, Perucca P, Ahnood A, Gill KP, Yan B, Churilov L, French CR, Desmond PM, Horne MK, Kiers L, Prawer S, Davis SM, Burkitt AN, Mitchell PJ, Grayden DB, May CN, O'Brien TJ. Minimally invasive endovascular stent-electrode array for high-fidelity, chronic recordings of cortical neural activity. Nat Biotechnol. 2016 Mar;34(3):320-7. doi: 10.1038/nbt.3428.






