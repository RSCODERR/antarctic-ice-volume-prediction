import numpy as np
import sys
import os

sys.path.insert(0, '.')
from scratch.test_thalweg import bed, thick, surf

print("Direct BedMachine variables along the thalweg:")
for i in range(15):
    print(f"cell {i:2d}: surf={surf[i]:7.1f}m, bed={bed[i]:7.1f}m, thick={thick[i]:7.1f}m, bed+thick={bed[i]+thick[i]:7.1f}m, diff={surf[i] - (bed[i]+thick[i]):7.1f}m")

print("\nLast 15 cells:")
for i in range(len(surf)-15, len(surf)):
    print(f"cell {i:2d}: surf={surf[i]:7.1f}m, bed={bed[i]:7.1f}m, thick={thick[i]:7.1f}m, bed+thick={bed[i]+thick[i]:7.1f}m, diff={surf[i] - (bed[i]+thick[i]):7.1f}m")
