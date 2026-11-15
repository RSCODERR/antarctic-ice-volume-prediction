import numpy as np

# In test_clean_conservation.py earlier:
# We had:
# Boundary Calving Outflow: 51437630445.2132 m^3/yr (47.168307 Gt/yr)
# Sum of div_F on ice domain: 51437630445.2132 m^3/yr (47.168307 Gt/yr)
# Predicted dM: 25.059632 Gt
# Actual dM:    25.059632 Gt
# Mass residual |Actual - Pred|: 1.77635683940025e-14 Gt !

# In that script, why was the mass residual 1.78e-14 Gt (exact)?
# Because in that script:
# dH = dt * (smb / RHO_ICE - div_F / cell_area)
# H_next = H + dH  (NO clipping with np.maximum, no thresholding)
# actual_dM = sum(rho_i * (H_next[ice_mask] - H[ice_mask]) * cell_area[ice_mask]) * 1e-12
# And predicted_dM = (smb_tot - boundary_calving) * dt!
# And it matched to 1.78e-14 Gt!
print("Exact discrete conservation holds identically when dH = dt * (smb/rho_i - div_F/A) is unclipped.")
