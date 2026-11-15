import pandas as pd

df = pd.read_csv('reports/tables/phase5_stage2_stability_and_conservation_tests.csv')

rows = []
for idx, r in df.iterrows():
    m_init_gt = float(r['Initial_Grounded_Mass_Gt'])
    m_final_gt = float(r['Final_Grounded_Mass_Gt'])
    smb_gt = float(r['Cumulative_SMB_Mass_Gt'])
    q_out_gt = float(r['Cumulative_Outflow_Mass_Gt'])
    bnd_gt = float(r['Cumulative_Boundary_Mass_Gt'])
    
    delta_m_gt = m_final_gt - m_init_gt
    
    m_init_kg = m_init_gt * 1.0e12
    m_final_kg = m_final_gt * 1.0e12
    delta_m_kg = delta_m_gt * 1.0e12
    smb_kg = smb_gt * 1.0e12
    q_out_kg = q_out_gt * 1.0e12
    bnd_kg = bnd_gt * 1.0e12
    
    # Continuous mass conservation: dM_gr/dt = SMB - Q_GL + dM_boundary
    # Residual: R = (M_final - M_init) - (SMB - Q_GL + Boundary)
    # Equivalently as requested: Delta_M - SMB + Q_GL - Boundary
    res_kg = delta_m_kg - smb_kg + q_out_kg - bnd_kg
    res_gt = res_kg * 1.0e-12
    rel_err = abs(res_kg) / m_init_kg
    max_step_res_kg = float(r['Max_Single_Step_Residual_kg'])
    
    print(f"=== {r['Experiment_ID']} ===")
    print(f"  M_init:   {m_init_kg:22.4f} kg  ({m_init_gt:12.6f} Gt)")
    print(f"  M_final:  {m_final_kg:22.4f} kg  ({m_final_gt:12.6f} Gt)")
    print(f"  Delta_M:  {delta_m_kg:22.4f} kg  ({delta_m_gt:12.6f} Gt)")
    print(f"  SMB:      {smb_kg:22.4f} kg  ({smb_gt:12.6f} Gt)")
    print(f"  Q_out:    {q_out_kg:22.4f} kg  ({q_out_gt:12.6f} Gt)")
    print(f"  Boundary: {bnd_kg:22.4f} kg  ({bnd_gt:12.6f} Gt)")
    print(f"  Prognostic Residual: {res_kg:15.6e} kg  ({res_gt:15.6e} Gt)")
    print(f"  Max Step Residual:   {max_step_res_kg:15.6e} kg")
    print(f"  Relative Error:      {rel_err:15.6e}")

