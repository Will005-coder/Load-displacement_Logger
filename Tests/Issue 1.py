#Test Script for issue 1 | Test back spooling and forward spooling
# Status: In Progress
# Stage: Generating a phantom signal; to be used later to test `cd``
# Approach: 
import calculate_displacement as cd
import numpy as np
import matplotlib.pyplot as plt


# Parameter Settings
n_steps = 200
start_val = 50
noise_scale = 1.5

slope = np.random.uniform(-0.2, 0.2)
trend = slope * np.arange(n_steps)
step_sizes = np.random.normal(0, noise_scale, n_steps)
random_walk = np.cumsum(step_sizes)

# generate phantom signal 
phantom_signal = start_val + trend + random_walk

# plot 
plt.figure(figsize=(10, 5))
plt.plot(phantom_signal, label=f"Phantom Signal (Slope: {slope:.3f})", color='b')
plt.plot(start_val + trend, label="Underlying Linear Trend", color='r', linestyle='--')
plt.title("Linearly Growing Randomized Trend Signal")
plt.xlabel("Time Step")
plt.ylabel("Signal Amplitude")
plt.legend()
plt.grid(True)
plt.show()
