# Neuromorphic-Decoding-of-Attenuated-Endovascular-Signals

# Overview

This repository contains a systems-level Python simulation of an ultra-low-power, event-driven neuromorphic pipeline designed for endovascular Brain-Computer Interfaces (BCIs).

Minimally invasive BCIs (like the Stentrode) offer exceptional safety profiles but suffer from severe high-frequency signal attenuation due to the capacitive filtering of the blood vessel wall. Furthermore, standard digital decoding (e.g., on-sensor DSPs or FPGAs) is often too power-hungry for micro-implants operating within strict thermal limits.

This project simulates a purely analog, hardware-efficient signal isolation pipeline. It models the biological tissue attenuation using a Randles equivalent circuit and utilizes the thermal dynamics of a VO₂ Mott Insulator to execute Leaky Integrate-and-Fire (LIF) spike encoding, entirely bypassing the 60 mV/decade Boltzmann limit of standard CMOS.

# System Architecture

The pipeline consists of four main continuous-time nodes:

1. Signal & Noise Synthesis: Generates an 80 Hz high-gamma motor intent burst buried in physiological $1/f$ pink noise.

2. Biological Interface (Tissue Attenuation): Models the blood vessel wall / endothelial layers as 1st-order and 2nd-order low-pass filters (capacitive RC networks).

3. Analog Front-End (AFE): A 2nd-order Butterworth bandpass filter (60–100 Hz) to isolate the high-gamma band.

4. Hardware Spike Encoder (VO₂ LIF): An event-driven Leaky Integrate-and-Fire neuron. The LIF leak time constant (tau) mathematically models the engineered thermal time constant (Rth, Cth) of a VO₂ memristor undergoing Joule heating, allowing it to act as a volatile threshold gatekeeper.

# Repository Contents

1. stentrode_pipeline.py

This script performs a rigorous statistical evaluation of the baseline neuromorphic pipeline.

Method: 
Runs a 200-trial Monte Carlo simulation across randomly generated 1/f noise profiles.

Optimization: 
Sweeps 40 different hardware voltage thresholds Vth.

Metric: 
Maximizes Youden's J statistic (TPR - FPR) on the Receiver Operating Characteristic (ROC) curve to find the absolute mathematically optimal firing threshold.

Output: 
Generates a composite image detailing the time-domain signal evolution, the ROC detection tradeoff with +-1 standard deviation bands, and the Youden optimization landscape.

<img width="1918" height="972" alt="image" src="https://github.com/user-attachments/assets/6783119a-e0ed-4b19-bc04-64adbaec8427" />


2. stentrode_stress_testing.py

This script stress-tests the hardware architecture against varying degrees of surgical success/failure.

Ideal Placement: 
Modeled as a single endothelial capacitive layer (1st-order low-pass, 100 Hz cutoff).

Poor Placement: 
Modeled as a thick fibrotic capsule or thick-walled vein (Cascaded 2nd-order low-pass, 50 Hz cutoff).

Output: 
Plots a comparative ROC curve proving the severe vulnerability of high-gamma signals to multi-layer tissue impedance, demonstrating why dynamic threshold calibration is strictly required in vivo.

<img width="1918" height="922" alt="image" src="https://github.com/user-attachments/assets/b6dc4b89-7d23-458d-9df9-66e3139e77f4" />





