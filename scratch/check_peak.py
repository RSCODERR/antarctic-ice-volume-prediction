import numpy as np
import sys
import os

sys.path.insert(0, '.')
from scratch.test_thalweg import surf, bed, thick

# Find peak
peak_idx = int(np.argmax(surf[:10]))
print(f"Summit peak is at cell {peak_idx}: surf={surf[peak_idx]:.1f}m")

# Check surface from peak to terminus
s_from_peak = surf[peak_idx:105]
ds = np.diff(s_from_peak)
print(f"Surface drops from {s_from_peak[0]:.1f}m to {s_from_peak[-1]:.1f}m")
print(f"Mean drop per 500m cell: {np.mean(ds):.2f}m")
print(f"Max reverse step: {np.max(ds):.2f}m, Min drop: {np.min(ds):.2f}m")

