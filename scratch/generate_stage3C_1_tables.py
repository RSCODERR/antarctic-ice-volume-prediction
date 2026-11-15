import os, csv, shutil

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

repo_tables = os.path.join('.', 'reports', 'tables')
brain_tables = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables'
os.makedirs(repo_tables, exist_ok=True)
os.makedirs(brain_tables, exist_ok=True)

# 1. Geometry and Observation Consistency Audit CSV
geom_obs_headers = [
    'Glacier_ID',
    'Glacier_Name',
    'Basin_ID',
    'Geometry_Source_and_Epoch',
    'Observation_Source_and_Epoch',
    'Epoch_Synchronization_Status',
    'Grounding_Line_Cell_Index',
    'Grounding_Line_Position_km',
    'GL_Ice_Thickness_m',
    'GL_Bed_Elevation_m',
    'GL_Surface_Slope',
    'Flotation_Thickness_Threshold_m',
    'Flotation_Status_at_GL',
    'Grounded_Cells_Count',
    'Floating_Cells_Count',
    'Observed_Velocity_Gate_ID',
    'Observed_Velocity_Sampling_Location',
    'Model_Sampling_Location',
    'Sampling_Displacement_km',
    'Model_Velocity_at_Gate_Location_m_yr',
    'Model_Velocity_at_GL_Sampling_m_yr',
    'Velocity_Representation_Type',
    'Vertical_Shear_Correction_Factor',
    'Reused_Ryder_Uncertainty_m_yr',
    'Independently_Supported_Uncertainty_m_yr',
    'Uncertainty_Support_Justification',
    'Comparison_Classification_Verdict'
]

geom_obs_rows = [
    [
        'FL_HPI_02',
        'Millett / Dyer Glacier System',
        'Hp-I (Palmer Land West)',
        'BedMachine v4.1 (REMA / OIB radar nominal 2014-2016)',
        'MEaSUREs InSAR 2011/2016 multi-year mosaic (Obs years: 2000, 2007-2009, 2013-2024)',
        'Synchronized (Nominal ~2011-2016 decadal alignment)',
        84,
        42.25,
        548.41,
        -445.55,
        '1.0442e-01 (10.44% slope)',
        499.48,
        'Grounded (H/Hf = 1.098; 10% above flotation)',
        85,
        25,
        'GATE_HP_02',
        'Flux Gate located 8.0 km upstream of grounding line (Distance ~34.25 km from divide)',
        'Cell 84 (Grounding line cell, Distance 42.25 km from divide)',
        '8.0 km downstream of actual observation gate',
        3511.42,
        3858.76,
        'Model = Depth-Integrated (u_bar); Obs = Satellite Surface InSAR (u_surf)',
        'u_bar in [0.80, 1.00] * u_surf (Glen n=3 vertical deformation allowance)',
        18.03,
        19.20,
        'InSAR instrumental error 12 m/yr + 15 m/yr cross-channel representation over 15.2 km gate width',
        'Conditionally Valid (8 km spatial sampling offset changes speed by 347 m/yr, but does not alter massive +1100% over-speeding verdict)'
    ],
    [
        'FL_IPPJ_03',
        'Flask / Leppard Glacier System',
        'Ipp-J (Graham Land East, Larsen C)',
        'BedMachine v4.1 (REMA / OIB radar nominal 2014-2016)',
        'MEaSUREs InSAR 2011/2016 multi-year mosaic (Obs years: 1996, 2002-2024)',
        'Synchronized (Continuous buttressed flow regime under Larsen C throughout 1996-2024)',
        58,
        29.25,
        699.78,
        -622.68,
        '1.1530e-02 (1.15% slope)',
        698.05,
        'Grounded (H/Hf = 1.002; right on threshold of hydrostatic flotation)',
        59,
        14,
        'GATE_IPJ_03',
        'Flux Gate located 7.0 km upstream of grounding line (Distance ~22.25 km from divide)',
        'Cell 58 (Grounding line cell, Distance 29.25 km from divide)',
        '7.0 km downstream of actual observation gate',
        157.56,
        125.76,
        'Model = Depth-Integrated (u_bar); Obs = Satellite Surface InSAR (u_surf)',
        'u_bar in [0.80, 1.00] * u_surf (Glen n=3 vertical deformation allowance)',
        18.03,
        28.50,
        'InSAR instrumental error 10 m/yr + 26.7 m/yr narrow fjord shear margin representation over 7.1 km gate width',
        'Conditionally Valid (7 km spatial offset changes speed from 158 to 126 m/yr, confirming severe under-speeding against 310 m/yr target)'
    ],
    [
        'FL_IPPJ_01',
        'Drygalski Glacier System',
        'Ipp-J (Graham Land East, Larsen A)',
        'BedMachine v4.1 (REMA / OIB radar nominal 2014-2016, 20 yrs post-collapse)',
        'ERS-1/2 post-collapse surge tracking (1995-1999) and decadal mean (Rott et al. 1996, 2002)',
        'Desynchronized (Severe 20-year lag between 1995 post-collapse surge velocity and 2015 readjusted geometry)',
        71,
        35.75,
        253.64,
        -184.80,
        '8.7370e-02 (8.74% slope)',
        207.17,
        'Grounded (H/Hf = 1.224; 22% above flotation)',
        72,
        5,
        'GATE_IPJ_DRY',
        'Discrete Larsen A embayment entrance gate (5.0 to 10.0 km upstream of calving margin)',
        'Cell 71 (Grounding line / terminal grounding zone, Distance 35.75 km from divide)',
        '5.0 to 8.0 km downstream of embayment entrance gate',
        127.80,
        177.13,
        'Model = Depth-Integrated (u_bar); Obs = Satellite Surface InSAR (u_surf)',
        'u_bar in [0.80, 1.00] * u_surf (Glen n=3 vertical deformation allowance)',
        18.03,
        45.75,
        'Post-collapse transient surge temporal variability +/-15% (Rott et al. 2002; Table final_scenario_definitions)',
        'Methodologically Compromised / Invalid (Severe epoch mismatch, transient surge relaxation unmodeled, and diagnostic solver did not converge)'
    ]
]

p_geom = os.path.join(repo_tables, 'phase5_stage3C_1_geometry_observation_audit.csv')
with open(p_geom, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(geom_obs_headers)
    w.writerows(geom_obs_rows)
shutil.copy2(p_geom, os.path.join(brain_tables, 'phase5_stage3C_1_geometry_observation_audit.csv'))

# 2. Numerical Convergence Audit CSV
num_conv_headers = [
    'Glacier_ID',
    'Glacier_Name',
    'Diagnostic_Solve_Iters',
    'Diagnostic_Picard_Residual',
    'Diagnostic_Convergence_Threshold',
    'Diagnostic_Solve_Converged',
    'Diagnostic_Unconverged_State_Accepted',
    'Static_Velocity_Depends_on_Unconverged_State',
    'Prognostic_Steps_Total',
    'Prognostic_Steps_Converged',
    'Prognostic_Unconverged_Steps_Count',
    'Prognostic_Unconverged_Steps_Pct',
    'Prognostic_Unconverged_Steps_Range',
    'Prognostic_Residual_Min',
    'Prognostic_Residual_Median',
    'Prognostic_Residual_Max',
    'Prognostic_Unconverged_States_Accepted',
    'Prognostic_Mass_Balance_Depends_on_Unconverged_States',
    'Discrete_Mass_Residual_kg',
    'Relative_Mass_Conservation_Error',
    'Numerical_Integrity_Verdict'
]

num_conv_rows = [
    [
        'FL_HPI_02',
        'Millett / Dyer Glacier System',
        35,
        '9.0073e-05',
        '1.0000e-04',
        True,
        'False (Diagnostic solve achieved convergence)',
        False,
        250,
        250,
        0,
        '0.0%',
        'None',
        'N/A',
        'N/A',
        '9.9953e-05',
        'False (100% of forward steps converged)',
        False,
        -1.5391,
        '2.0304e-15',
        'Fully Converged Momentum & Exact Mass Conservation (< 1.6 kg residual)'
    ],
    [
        'FL_IPPJ_03',
        'Flask / Leppard Glacier System',
        35,
        '9.3614e-05',
        '1.0000e-04',
        True,
        'False (Diagnostic solve achieved convergence)',
        False,
        250,
        206,
        44,
        '17.6%',
        'Steps 14 to 249 (Time 0.28 to 4.98 yr)',
        '1.2150e-04',
        '2.1681e-04',
        '4.2878e-04',
        'True (Accepted unconditionally by FVContinuitySolver.step without rollback)',
        True,
        +0.0005,
        '2.5648e-18',
        'Valid Static Velocity; Prognostic Mass Balance Dependent on 44 Unconverged Picard Steps'
    ],
    [
        'FL_IPPJ_01',
        'Drygalski Glacier System',
        80,
        '1.9937e-04',
        '1.0000e-04',
        False,
        'True (Accepted at iter 80 limit-cycle oscillation between 2.01e-4 and 4.52e-4)',
        True,
        250,
        197,
        53,
        '21.2%',
        'Steps 0 to 249 (Time 0.00 to 4.98 yr)',
        '1.3155e-04',
        '3.7101e-04',
        '1.4225e-03',
        'True (Accepted unconditionally by FVContinuitySolver.step without rollback)',
        True,
        +0.3774,
        '2.2560e-15',
        'Momentum Non-Convergence: Both Static Velocity and Prognostic Run Depend on Unconverged States'
    ]
]

p_num = os.path.join(repo_tables, 'phase5_stage3C_1_numerical_convergence_audit.csv')
with open(p_num, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(num_conv_headers)
    w.writerows(num_conv_rows)
shutil.copy2(p_num, os.path.join(brain_tables, 'phase5_stage3C_1_numerical_convergence_audit.csv'))

# 3. Regional Mass-Budget Reconciliation CSV
reg_mass_headers = [
    'Accounting_Entity_or_Glacier',
    'Glacier_ID',
    'Basin_ID',
    'Spatial_Domain_km2',
    'Domain_A_Area_Coverage_Pct',
    'Accounting_Time_Interval_yr',
    'Cumulative_Grounded_Delta_M_Gt',
    'Annual_Grounded_Mass_Rate_Gt_yr',
    'Cumulative_SMB_Gt',
    'Annual_SMB_Rate_Gt_yr',
    'Cumulative_GL_Outflow_Gt',
    'Annual_GL_Outflow_Rate_Gt_yr',
    'Cumulative_Flotation_Remap_Gt',
    'Annual_Remap_Rate_Gt_yr',
    'Discrete_Mass_Residual_kg',
    'Contribution_to_Sample_4Glacier_Loss_Pct',
    'Contribution_to_Regional_IMBIE3_Dynamic_Loss_Pct',
    'Accounting_Reconciliation_Finding'
]

reg_mass_rows = [
    [
        'Ryder / Bertram Glacier System',
        'FL_HPI_01',
        'Hp-I',
        42150.20,
        '19.51%',
        5.0,
        -6.3277,
        -1.2655,
        +0.8183,
        +0.1637,
        +7.1158,
        +1.4232,
        -0.0302,
        -0.0060,
        -0.9380,
        '12.14% (12.16% of outflow)',
        '4.08%',
        'Stage 3B.1 Calibrated baseline; dynamic loss balanced by Western Palmer Land accumulation'
    ],
    [
        'Millett / Dyer Glacier System',
        'FL_HPI_02',
        'Hp-I',
        38420.50,
        '17.78%',
        5.0,
        -41.9198,
        -8.3840,
        +1.3326,
        +0.2665,
        +43.2312,
        +8.6462,
        -0.0212,
        -0.0042,
        -1.5391,
        '80.44% of mass loss (78.99% of outflow; 80.84% reported)',
        '24.77%',
        'Exact source of 80.8% claim: Millett net loss (-8.38 Gt/yr) divided by 4-flowline sample sum (-10.37 Gt/yr)'
    ],
    [
        'Flask / Leppard Glacier System',
        'FL_IPPJ_03',
        'Ipp-J',
        16880.50,
        '7.81%',
        5.0,
        -3.3157,
        -0.6631,
        +0.3828,
        +0.0766,
        +3.4663,
        +0.6933,
        -0.2323,
        -0.0465,
        +0.0005,
        '6.36% (6.33% of outflow)',
        '1.99%',
        'Severely under-discharging due to excessive Palmer Land basal friction in narrow alpine fjord'
    ],
    [
        'Drygalski Glacier System',
        'FL_IPPJ_01',
        'Ipp-J',
        15120.30,
        '7.00%',
        5.0,
        -0.5489,
        -0.1098,
        +0.3581,
        +0.0716,
        +0.9041,
        +0.1808,
        -0.0030,
        -0.0006,
        +0.3774,
        '1.05% (1.65% of outflow)',
        '0.52%',
        'Severely under-discharging; unable to sustain observed post-1995 Larsen A unbuttressed surge'
    ],
    [
        '4-Flowline Sample Aggregate',
        'SAMPLE_SUM',
        'Hp-I + Ipp-J',
        112571.50,
        '52.10%',
        5.0,
        -52.1122,
        -10.4224,
        +2.8919,
        +0.5784,
        +54.7174,
        +10.9435,
        -0.2867,
        -0.0573,
        -2.0992,
        '100.00% (Denominator of 80.8% claim = -10.366 Gt/yr)',
        '31.35%',
        'Represents 52.1% of Domain A grounded area. Does NOT represent full regional Antarctic Peninsula dynamic total'
    ],
    [
        'Unmodeled Domain A Remainder',
        'REMAINDER',
        'Domain A',
        103490.67,
        '47.90%',
        5.0,
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'Unmodeled',
        'N/A',
        'N/A',
        '68.65% (Required to match IMBIE3)',
        'Comprises Crane, Flanders Bay, Whirlwind, Evans, and interior plateaus (47.9% of total ice sheet area)'
    ],
    [
        'IMBIE3 Regional Benchmark',
        'IMBIE3_AP',
        'Domain A',
        216062.17,
        '100.00%',
        20.0,
        'N/A',
        '-31.25 +/- 8.20',
        'N/A',
        '+3.66 +/- 10.50',
        'N/A',
        '+34.91 +/- 12.50',
        'N/A',
        'N/A',
        'N/A',
        'N/A',
        '100.00%',
        'Full regional Antarctic Peninsula mass balance (Otosaka et al. 2023). Multi-flowline model matches 31.4% of total dynamic anomaly'
    ]
]

p_reg = os.path.join(repo_tables, 'phase5_stage3C_1_regional_mass_reconciliation.csv')
with open(p_reg, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(reg_mass_headers)
    w.writerows(reg_mass_rows)
shutil.copy2(p_reg, os.path.join(brain_tables, 'phase5_stage3C_1_regional_mass_reconciliation.csv'))

# 4. Updated Risk Register CSV
risk_headers = [
    'Risk_ID',
    'Category',
    'Risk_Description',
    'Severity',
    'Likelihood',
    'Mitigation_Strategy',
    'Residual_Risk',
    'Stage_3C_1_Audit_Status'
]

risk_rows = [
    [
        'RSK_VAL_01',
        'Scientific Transferability & Attribution',
        'Attributing model-observation discrepancies solely to spatial variation in C_bed without accounting for geometric, structural, and boundary condition confounding factors',
        'CRITICAL',
        'HIGH',
        'Strictly distinguish Claim A (Ryder parameter failed to match obs), Claim B (model did not demonstrate transferability), and Claim C (C_bed variation is physically necessary). Reject claims of universal physical constants or definitive falsification of physical laws.',
        'LOW (Clarified)',
        'CORRECTED: Scientific claims rigorously delineated into empirical facts versus unproven physical hypotheses.'
    ],
    [
        'RSK_NUM_07',
        'Numerical Momentum Convergence',
        'SSA Picard non-linear solver experiences limit-cycle oscillation at 80 iterations in steep alpine margins (Drygalski diagnostic solve res 1.99e-4; 53 forward steps; Flask 44 forward steps)',
        'HIGH',
        'CERTAIN',
        'Unconverged states explicitly audited and documented as numerical limitation. Never cite mass conservation as proof of momentum convergence. Preserve convergence threshold at 1.0e-4. Recommend Newton-Krylov / pseudo-transient continuation for Stage 4.',
        'MEDIUM (Bounded)',
        'BOUNDED & CLASSIFIED: Unconverged states transparently logged; velocity comparisons classified accordingly.'
    ],
    [
        'RSK_REG_02',
        'Regional Mass Accounting',
        'Confusing a subset of 4 modeled flowlines with the full regional Antarctic Peninsula dynamic loss denominator (the 80.8% artifact)',
        'MEDIUM',
        'VERY LOW',
        'Formally report the exact denominator (-10.366 Gt/yr sample sum). Distinguish 4-flowline sample dynamic loss (10.94 Gt/yr) from regional IMBIE3 dynamic loss anomaly (34.91 Gt/yr). Enforce strict spatial domain accounting.',
        'NONE (Resolved)',
        'RECONCILED: Exact denominator identified and dimensional consistency established.'
    ],
    [
        'RSK_GEO_03',
        'Geometry & Observation Synchronization',
        'Temporal epoch mismatch (Drygalski 20-yr lag between 1995 surge and 2015 BedMachine v4.1 geometry) and spatial displacement between observation flux gates and grounding-line model sampling',
        'HIGH',
        'CERTAIN',
        'Quantified spatial gradients: 8.0 km displacement in Millett shifts speed by 347 m/yr; 7.0 km displacement in Flask shifts speed by 32 m/yr. Drygalski classified as methodologically invalid due to severe post-collapse transient relaxation mismatch.',
        'LOW (Classified)',
        'CLASSIFIED: Millett/Flask classified as conditionally valid; Drygalski classified as invalid comparison.'
    ],
    [
        'RSK_UNC_04',
        'Observational Uncertainty Support',
        'Improperly reusing Ryder 18.03 m/yr combined uncertainty across all validation glaciers without glacier-specific justification',
        'MEDIUM',
        'CERTAIN',
        'Independently derived observational uncertainties: Millett +/-19.2 m/yr; Flask +/-28.5 m/yr; Drygalski +/-45.8 m/yr (+/-15% surge envelope). Re-evaluated z-scores under independent uncertainties.',
        'NONE (Corrected)',
        'CORRECTED: Glacier-specific uncertainty provenance documented and applied.'
    ],
    [
        'RSK_GOV_05',
        'Governance Scope Containment',
        'Unauthorized parameter refitting, tuning against validation targets, Crane calibration, ML training, ISMIP6 tuning, or 2100 projections',
        'CRITICAL',
        'VERY LOW',
        'Zero parameter modification permitted during forensic audit. All parameters remain locked at frozen Stage 3B.1 values. Mandatory governance hard stop strictly maintained.',
        'NONE',
        'STRICTLY MAINTAINED: Zero parameters changed. All governance boundaries preserved.'
    ]
]

p_risk = os.path.join(repo_tables, 'phase5_stage3C_1_risk_register.csv')
with open(p_risk, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(risk_headers)
    w.writerows(risk_rows)
shutil.copy2(p_risk, os.path.join(brain_tables, 'phase5_stage3C_1_risk_register.csv'))

print("All Stage 3C.1 audit tables successfully generated and mirrored.")

