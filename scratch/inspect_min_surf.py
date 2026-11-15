import numpy as np
import sys

sys.path.insert(0, '.')
from scratch.test_thalweg import surf, bed, thick

min_idx = np.argmin(surf)
print(f"Minimum surface elevation along line: cell {min_idx}, surf={surf[min_idx]:.1f}m, bed={bed[min_idx]:.1f}m, thick={thick[min_idx]:.1f}m")
print("\nSurface progression from cell 0 to min_idx:")
for i in range(0, min_idx + 1, 10):
    print(f"cell {i:3d}: surf={surf[i]:7.1f}m, bed={bed[i]:7.1f}m, thick={thick[i]:7.1f}m")

