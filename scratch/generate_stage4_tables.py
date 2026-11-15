import os, csv, shutil

if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

repo_tables = os.path.join('.', 'reports', 'tables')
brain_tables = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables'
os.makedirs(repo_tables, exist_ok=True)
os.makedirs(brain_tables, exist_ok=True)

# 1. Architecture Comparison Matrix
matrix_headers = [
    'Architecture_Option',
    'Option_Name',
    'Governing_Equations',
    'Stress_Balance_Assumptions',
    'Lateral_Drag_Representation',
    'Tributary_Flow_Treatment',
    'Grounding_Line_Dynamics',
    'Moving_Geometry_and_Continuity',
    'Basal_Traction_Representation',
    'Ice_Shelf_Buttressing_Coupling',
    'Surface_Mass_Balance_Coupling',
    'Computational_Requirements',
    'Domain_A_Grounded_Footprint_Coverage',
    'Software_Engineering_and_Reproducibility',
    'Principal_Scientific_Limitations',
    'Overall_Feasibility_Verdict'
]

matrix_rows = [
    [
        'Option A',
        'Retained 1D SSA Flowlines with Enhanced Empirical Lateral Drag',
        '1D SSA: d/dx(4 H nu du/dx) - beta_b u - (2H/W) tau_lat = rho_i g H ds/dx',
        'Centerline longitudinal stretching and basal/lateral resistance; zero transverse stress gradient',
        'Parameterized body force: tau_lat = (u / (mu B W))^(1/n) with empirical shape factor kappa_shape',
        'Ignored or added as uncoupled 1D scalar mass source term S_trib(x); zero momentum exchange',
        '1D sub-grid moving boundary using Schoof or kinematic flux Q_GL = H W u',
        '1D Finite-Volume continuity: dH/dt + d(uH)/dx = SMB along 1D line',
        'Catchment-uniform or piecewise 1D scalar C_bed(x)',
        'Scalar back-stress parameter theta_buttress applied at downstream calving face',
        '1D along-flowline accumulation profile from RACMO / elevation lapse rate',
        'Negligible (< 1 s per 5-yr simulation on single CPU thread)',
        'Partial (50-60% via discrete flowlines; requires 40-50% unmodeled remainder)',
        'Extremely simple; existing codebase; high reproducibility but low physical validity',
        'Fails in narrow fjords where lateral shear margins dominate (Flask -49%, Millett +1100%); leaves half of Domain A unmodeled',
        'REJECTED (Structurally inadequate to resolve 2D fjord physics and regional mass balance)'
    ],
    [
        'Option B',
        'Extended 1D Multi-Flowline Branching Network with Explicit Tributaries',
        '1D SSA solved across directed tree-graph branches with nodal mass/momentum matching at junctions',
        '1D longitudinal stress along branches; normal stress / flux conservation enforced at junction nodes',
        'Parameterized lateral body force on each individual branch',
        'Explicit 1D branch convergence: sum(Q_in) = Q_out at nodes; momentum jump condition across junctions',
        '1D GL migration on the main outlet trunk',
        'Branch-wise 1D FV continuity with nodal boundary flux balancing',
        'Branch-specific scalar C_bed_k for each tributary and trunk',
        'Shelf buttressing applied at terminal trunk calving front',
        'Branch-specific accumulation profiles integrated over tributary sub-catchments',
        'Low (< 5 s per simulation on CPU)',
        'Partial-to-Moderate (65-75% coverage; still leaves slow interior divides unmodeled)',
        'High code complexity (graph traversal, moving branch nodes); brittle topology when flow divides shift',
        'Still relies on parameterized 1D lateral drag; fails under dynamic thinning where ice divides migrate; cannot resolve curved 2D grounding lines',
        'REJECTED (Excessive architectural complexity without eliminating 1D physical approximations)'
    ],
    [
        'Option C',
        '2D Depth-Integrated Shallow-Shelf Approximation (2D SSA) [RECOMMENDED]',
        '2D Elliptic SSA system: div(2 H nu (2 eps_dot + tr(eps_dot) I)) - beta_b u = rho_i g H grad(s)',
        'Depth-integrated horizontal membrane stresses; vertical shear neglected (sliding dominant in streams) or hybrid SSA+SIA in interior',
        'NATURALLY RESOLVED: Transverse shear margins d/dy(2 H nu du/dy) and wall friction arise organically from 2D spatial stress tensor',
        'NATURALLY RESOLVED: Tributary convergence, lateral compression, and flow divergence handled directly by 2D continuum equations',
        'Continuous 2D grounding-line contact problem; hydrostatic flotation mask updated dynamically on 2D mesh with sub-grid flux parameterization',
        '2D Conservative Finite-Volume continuity: dH/dt + div(H u) = SMB across entire 2D grid',
        'Spatially continuous 2D basal traction field C_bed(x,y) with Tikhonov/TV regularization or catchment-partitioned zones',
        '2D shelf back-pressure tensor sigma_nn naturally transmitted across grounding-line boundary from floating shelf cavity',
        '2D spatiotemporal climate forcing: daily/monthly RACMO2.3p2 SMB(x,y,t) mapped directly to 500m grid',
        'Moderate (10-30 s per nonlinear solve; 15-45 min for 5-yr simulation; 2-4 hrs for century projection on 8-core workstation)',
        'COMPLETE: 100% coverage of Domain A (216,062.17 km², 866,358 cells); zero unmodeled remainder',
        'High maintainability: pure Python/SciPy/PETSc implementation; fully auditable, vectorized, and locally executable in workspace',
        'Neglects vertical shear in cold, slow interior ice domes (mitigated via hybrid SIA-SSA coupling); requires 2D sparse matrix linear solvers',
        'STRONGLY RECOMMENDED (Optimal balance of physical fidelity, complete Domain A coverage, and autonomous reproducibility)'
    ],
    [
        'Option D',
        'Higher-Fidelity Community Ice-Sheet Model (ISSM / Ua / Elmer/Ice / BISICLES / MALI)',
        '3D Blatter-Pattyn (First-Order) or Full Stokes equations with non-linear rheology and hydrostatic pressure coupling',
        'Resolves full 3D stress tensor (longitudinal, transverse, vertical shear, and bridging stresses)',
        'Full 3D representation of lateral drag and shear heating across bedrock walls',
        'Full 3D continuum resolving non-hydrostatic junction dynamics',
        'High-resolution adaptive mesh refinement (AMR down to 100m) or sub-element flotation parameterization',
        '3D moving surface and mesh ALE (Arbitrary Lagrangian-Eulerian) deformation',
        'Inversion of 2D basal friction coefficient using adjoint optimization',
        'Full 2D/3D viscoelastic/viscoplastic ice shelf cavity coupling',
        'Direct 2D/3D climate and ocean cavity thermal coupling',
        'High to Extreme (100-1000s of CPU core-hours per century projection; requires supercomputer MPI clusters)',
        'Complete 100% coverage of Domain A',
        'Low reproducibility in local workspace: massive external C++/Fortran dependencies, PETSc/MPI compilation, proprietary/complex toolchains',
        'Black-box dependency; unfeasible for rapid iterative testing, CI/CD automated verification, and lightweight local agent execution',
        'RESERVED AS EXTERNAL BENCHMARK (Utilize published outputs as independent validation, not primary engine)'
    ]
]

p_mat = os.path.join(repo_tables, 'phase5_stage4_architecture_comparison_matrix.csv')
with open(p_mat, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(matrix_headers)
    w.writerows(matrix_rows)
shutil.copy2(p_mat, os.path.join(brain_tables, 'phase5_stage4_architecture_comparison_matrix.csv'))

# 2. Data Availability and Gap Inventory
data_headers = [
    'Dataset_Identifier',
    'Dataset_Name',
    'Data_Provider_and_Authority',
    'Official_DOI_or_Source_URL',
    'Current_Availability_Status',
    'Spatial_Resolution_and_CRS',
    'Temporal_Coverage_and_Epoch',
    'Core_Variables_Used',
    'Licensing_and_Access_Requirements',
    'Primary_Scientific_Purpose_in_Stage_4',
    'Storage_Footprint_and_Format'
]

data_rows = [
    [
        'DS_BM4_01',
        'BedMachine Antarctica Version 4.1',
        'NASA NSIDC DAAC / UC Irvine (Morlighem et al.)',
        'doi:10.5067/F1BVDPTJFLC7',
        'AVAILABLE IN WORKSPACE (data/raw & data/processed)',
        '500 m grid, EPSG:3031',
        '1970–2019 (Nominal 2014–2016 REMA / OIB radar epoch)',
        'bed, surface, thickness, mask, firn, errbed',
        'Open Access / NASA Earthdata (CC-BY 4.0)',
        'Authoritative subglacial topography, initial ice thickness, and grounding mask across Domain A',
        '1.14 GB NetCDF (Raw) / 371 MB NetCDF (Aligned)'
    ],
    [
        'DS_BM3_02',
        'Bedmap3 Subglacial Topography',
        'British Antarctic Survey (Fremand et al. 2023)',
        'doi:10.5285/71537389-113C-419B-BC66-0010E16FF72A',
        'AVAILABLE IN WORKSPACE (data/raw & data/processed)',
        '500 m grid, EPSG:3031',
        '1958–2022 multi-decadal radar survey compilation',
        'bm3_bed, bm3_surface, bm3_thickness, bm3_masks, bm3_thickness_uncertainty',
        'Open Access / UK Polar Data Centre (CC-BY 4.0)',
        'Independent cross-validation of BedMachine bathymetry and bedrock elevation uncertainty mapping',
        '1.72 GB GeoTIFFs (Raw) / 20 MB GeoTIFFs (Processed)'
    ],
    [
        'DS_IMB_03',
        'IMBIE Regional Basin Delineations & Reconciled Mass Balance',
        'ESA / NASA IMBIE Team (Otosaka et al. 2023)',
        'doi:10.5194/essd-15-2887-2023',
        'AVAILABLE IN WORKSPACE (data/raw & data/processed)',
        'Vector Shapefile & 1km/5km/10km NetCDF, EPSG:3031',
        '1992–2020 (Decadal reconciled satellite mass balance)',
        'Basin boundaries (Hp-I, I-Ipp, Ipp-J), total mass balance time series, gravimetry/altimetry partitions',
        'Open Access / ESA IMBIE (CC-BY 4.0)',
        'Defines authoritative boundaries of Domain A and provides top-level regional mass loss benchmark',
        '28 MB Shapefile/NetCDF / 0.1 MB CSV'
    ],
    [
        'DS_ISM_04',
        'ISMIP6 Antarctic Projections Archive',
        'NASA GSFC / CMIP6 ISMIP6 (Seroussi et al. 2020)',
        'doi:10.5194/tc-14-3033-2020',
        'AVAILABLE IN WORKSPACE (data/raw & data/processed)',
        'Basin scalar time series and multi-model metrics',
        '2015–2100 under CMIP5/CMIP6 emission pathways',
        'Ice volume above flotation (VAF), grounded area, dynamic mass anomaly, control drift',
        'Open Access / CMIP6 (CC-BY 4.0)',
        'Strictly external validation benchmark; never used for model tuning or calibration',
        '31 MB ZIP / 7.3 MB Processed CSV'
    ],
    [
        'DS_ITS_05',
        'ITS_LIVE Regional Ice Velocity Mosaics (Antarctic Peninsula)',
        'NASA JPL / MEaSUREs (Gardner et al.)',
        'doi:10.5067/6II6VW8LLWJ7',
        'REQUIRED ACQUISITION (Targeted Acquisition in Stage 4.1)',
        '120 m and 240 m mosaic, EPSG:3031',
        '1985–2022 annual and multi-year velocity composites',
        'v, vx, vy, err_v (surface velocity components and error fields)',
        'Open Access / NASA Earthdata (CC-BY 4.0)',
        'Full 2D surface velocity field for 2D SSA model evaluation, shear margin mapping, and inversion',
        '~350 MB NetCDF (Peninsula crop)'
    ],
    [
        'DS_MEA_06',
        'MEaSUREs InSAR Grounding Line & Annual Velocity Mosaic (NSIDC-0484 / NSIDC-0754)',
        'NASA NSIDC DAAC (Rignot, Mouginot, Scheuchl)',
        'doi:10.5067/D7AKTGKO8DH3',
        'REQUIRED ACQUISITION (Targeted Acquisition in Stage 4.1)',
        '450 m grid / Vector shapefiles, EPSG:3031',
        '1996, 2000, 2011, 2016 multi-year InSAR composites',
        'vx, vy, v, spatial error, multi-epoch DInSAR grounding lines',
        'Open Access / NASA Earthdata (CC-BY 4.0)',
        'Empirical grounding line positions across 1996-2016 to validate 2D contact migration without circularity',
        '~180 MB NetCDF / Vector'
    ],
    [
        'DS_RAC_07',
        'RACMO2.3p2 Surface Mass Balance & Firn Densification (Antarctic Peninsula)',
        'Utrecht University IMAU (van Wessem et al. 2018)',
        'doi:10.5194/tc-12-1479-2018',
        'REQUIRED ACQUISITION (Targeted Acquisition in Stage 4.1)',
        '5.5 km native rotated pole grid, interpolated to 500 m EPSG:3031',
        '1979–2022 monthly and annual time series',
        'smb, precip, sublimation, runoff, snowmelt, firn_air_depth',
        'Academic Open Access / IMAU Climate Data Request',
        'Spatially distributed 2D climate forcing and firn air content to isolate solid ice volume change',
        '~450 MB NetCDF (1979–2022 monthly AP subset)'
    ],
    [
        'DS_ALT_08',
        'Satellite Radar & Laser Altimetry Elevation Change (CryoSat-2 & ICESat-2)',
        'CPOM / NASA GSFC (Shepherd et al. 2019; Smith et al. 2020)',
        'doi:10.1126/science.aaz5845',
        'REQUIRED ACQUISITION (Targeted Acquisition in Stage 4.1)',
        '500 m and 1 km gridded rate of elevation change (dh/dt)',
        '2003–2020 multi-mission altimetry',
        'dh_dt, err_dh_dt, lagrangian elevation change rates',
        'Open Access / CPOM & NSIDC (CC-BY 4.0)',
        'Independent observational benchmark for regional dynamic thinning rate validation',
        '~120 MB GeoTIFF / NetCDF'
    ]
]

p_data = os.path.join(repo_tables, 'phase5_stage4_data_availability_inventory.csv')
with open(p_data, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(data_headers)
    w.writerows(data_rows)
shutil.copy2(p_data, os.path.join(brain_tables, 'phase5_stage4_data_availability_inventory.csv'))

# 3. Model Risk Register
risk_headers = [
    'Risk_ID',
    'Risk_Category',
    'Risk_Description',
    'Severity',
    'Likelihood',
    'Architectural_Impact',
    'Mitigation_Strategy',
    'Residual_Risk_Level',
    'Stage_4_Governance_Status'
]

risk_rows = [
    [
        'RSK_ARCH_01',
        'Model Architecture & Lateral Shearing',
        '1D flowline models fundamentally fail to resolve 2D transverse shear margins, tributary confluences, and curved grounding lines',
        'CRITICAL',
        'CERTAIN',
        'Severe velocity errors in narrow fjords (-50% in Flask) and troughs (+1100% in Millett)',
        'Transition to 2D Depth-Integrated SSA (Option C), resolving lateral stress tensors div(2H nu eps_dot) on a native 500m mesh',
        'LOW (Mitigated)',
        'CORE ARCHITECTURAL REDESIGN: Eliminates 1D lateral drag approximations'
    ],
    [
        'RSK_NUM_08',
        'Non-linear Solver Convergence & Stagnation',
        'Picard iteration exhibits limit-cycle oscillations (Drygalski iter 80 residual 1.99e-4; Flask 44 unconverged steps)',
        'HIGH',
        'HIGH',
        'Momentum equations fail to close, potentially propagating unphysical velocities into continuity updates',
        'Deploy Preconditioned Inexact Newton-Krylov (PIN-K) with backtracking line-search, adaptive pseudo-transient continuation (PTC), and strict rollback on tolerance violation',
        'LOW (Controlled)',
        'SOLVER INTEGRITY MANDATE: Eliminates unconditional acceptance of unconverged states'
    ],
    [
        'RSK_REG_03',
        'Domain A Mass Accounting Coverage Gap',
        'Flowline models leave 47.9% of Domain A unmodeled, distorting regional mass balance (the 80.8% sample artifact)',
        'CRITICAL',
        'CERTAIN',
        'Regional mass balance is mathematically incomplete, confounding sample dynamic loss with regional totals',
        'Adopt 2D SSA model covering 100% of Domain A (866,358 cells) partitioned into hydrologic catchments with explicit interior ice divide flux accounting',
        'NONE (Resolved)',
        'FULL BASIN COVERAGE: Resolves 100% of Domain A without unmodeled remainder'
    ],
    [
        'RSK_GEO_04',
        'Geometry & Observation Temporal Mismatch',
        'Comparing post-collapse transient velocities (Drygalski 1995 surge) against post-readjustment 2015 BedMachine geometry',
        'HIGH',
        'HIGH',
        'Falsely rejects physical models due to 20-year lag in geometric driving stress and surface slope',
        'Enforce strict epoch matching: exclude desynchronized post-collapse transient cases from static validation; match BedMachine 2014-2016 geometry with synchronous 2014-2016 InSAR velocity mosaics',
        'LOW (Enforced)',
        'PROTOCOL INTEGRITY RULE: Zero temporal mixing of mismatched physical states'
    ],
    [
        'RSK_IDEN_05',
        'Parameter Degeneracy & Overfitting',
        'Over-parameterizing 2D basal traction field C_bed(x,y) leading to unconstrained equifinality and overfitting',
        'HIGH',
        'MEDIUM',
        'Fitted traction fields lack physical realism and diverge during 2100 forward prognostic runs',
        'Implement Tikhonov spatial regularization with L-curve criterion; constrain C_bed within geologically justified priors; test catchment-partitioned vs continuous fields',
        'MEDIUM (Bounded)',
        'IDENTIFIABILITY GOVERNANCE: Parameter search strictly bounded by literature and L-curve'
    ],
    [
        'RSK_GOV_06',
        'Scope Boundaries & Premature Execution',
        'Unauthorized calibration of Crane/Flanders, ML training, ISMIP6 tuning, or 2100 forward projections during Stage 4.0 design',
        'CRITICAL',
        'VERY LOW',
        'Violates stage-gate governance and invalidates independent scientific review',
        'Strict design-only boundary maintained. Zero solver implementation or recalibration in Stage 4.0. Hard stop condition enforced.',
        'NONE',
        'STRICTLY MAINTAINED: Stage 4.0 remains 100% design and protocol architecture'
    ]
]

p_risk = os.path.join(repo_tables, 'phase5_stage4_risk_register.csv')
with open(p_risk, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(risk_headers)
    w.writerows(risk_rows)
shutil.copy2(p_risk, os.path.join(brain_tables, 'phase5_stage4_risk_register.csv'))

# 4. Parameter Identifiability Plan
iden_headers = [
    'Parameter_Name',
    'Parameter_Symbol',
    'Physical_Interpretation',
    'Spatial_Representation_Model',
    'Prior_Literature_Bounds',
    'Observational_Constraints_Used',
    'Mathematical_Identifiability_Status',
    'Degeneracy_and_Equifinality_Risk',
    'Identifiability_Resolution_Protocol'
]

iden_rows = [
    [
        'Basal Traction Coefficient (Ryder Reference)',
        'C_bed,HpI',
        'Macroscopic basal sliding resistance in Western Palmer Land marine trough',
        'Scalar constant (Frozen Historical Reference)',
        '1.0e+06 to 5.0e+07 Pa*(m/s)^(-1/3)',
        'Ryder Glacier MEaSUREs InSAR velocity profile (Cells 10 to 45)',
        'Identifiable (Conditionally locked to frozen Stage 3B.1 value: 8.168e+06)',
        'Degenerate with effective viscosity B and ice thickness H if unconstrained',
        'FROZEN HISTORICAL BASELINE: Maintained as benchmark; never refitted in Stage 4'
    ],
    [
        'Catchment-Partitioned Basal Traction',
        'C_bed,catchment',
        'Discrete catchment-level basal slipperiness reflecting regional bedrock geology and till state',
        'Piecewise-constant scalar per major glacial catchment (e.g., Ryder, Millett, Flask, Crane)',
        '1.0e+05 to 1.0e+08 Pa*(m/s)^(-1/3)',
        'Catchment-averaged InSAR surface velocity and flux gate profiles',
        'Practically Identifiable (Assuming known BedMachine v4.1 geometry and fixed Glen A)',
        'Moderate equifinality with lateral wall drag in narrow fjords (< 7 km)',
        'Identified via 2D SSA inversion using cross-channel velocity profiles to separate lateral from basal drag'
    ],
    [
        'Continuous 2D Basal Traction Field',
        'C_bed(x,y)',
        'Spatially varying basal traction field capturing subglacial bed transition zones',
        'Continuous 2D field on 500 m mesh with Tikhonov L-curve regularization',
        'Log10(C_bed) in [4.5, 8.5] Pa*(m/s)^(-1/3)',
        '2D ITS_LIVE surface velocity mosaic and MEaSUREs velocity gradients',
        'Conditionally Identifiable (Ill-posed without spatial regularization)',
        'High degeneracy: velocity errors map directly into high-frequency bed friction artifacts',
        'Enforce spatial smoothness penalty alpha * ||grad(C_bed)||^2; select regularization parameter alpha via L-curve'
    ],
    [
        'Effective Pressure Exponent / Hydrology',
        'q_hyd, p_hyd',
        'Coupling between subglacial water pressure and basal sliding (Budd / Schoof sliding laws)',
        'Empirical subglacial hydrological parameter',
        'q in [0, 1], p in [0, 1]',
        'Requires subglacial water pressure observations (unavailable in AP)',
        'UNIDENTIFIABLE from available remote-sensing observations',
        'Severe equifinality with C_bed and bed topography',
        'EXCLUDE FROM PRIMARY INVERSION: Set to standard Weertman (q=0) or fixed overburden hydrostatic N = rho_i g H - rho_w max(0, -b)'
    ],
    [
        'Ice Rheology Rate Factor',
        'A_glen',
        'Creep rate factor in Glen flow law (T = -10 deg C to -2 deg C)',
        'Temperature-dependent Arrhenius field (Paterson & Budd 1982)',
        '1.0e-25 to 5.0e-24 Pa^(-3) s^(-1)',
        'Borehole ice temperature profiles (extremely sparse on AP)',
        'Conditionally Identifiable (Degenerate with basal sliding in fast streams)',
        'Direct equifinality: softer ice (higher A) mimics slippery bed (lower C_bed)',
        'FREEZE TO STANDARDIZED GLACIOLOGICAL VALUES: A = 3.5e-25 Pa^(-3) s^(-1) (calibrated to -5 deg C isotherm); do not co-invert with C_bed'
    ],
    [
        'Grounding Line Flux Prefactor',
        'C_schoof',
        'Dimensionless flux multiplier for Schoof analytical grounding-line boundary condition',
        'Global scalar parameter',
        '0.50 to 1.50 (Standard Schoof theoretical baseline = 0.61)',
        'Grounding-line retreat rates from multi-epoch DInSAR (1996–2016)',
        'Practically Identifiable in transient runs; unidentifiable in static diagnostic solves',
        'Degenerate with ice shelf buttressing back-stress parameter theta_buttress',
        'Keep frozen at C_schoof = 0.61 during static geometry setup; evaluate sensitivity strictly in transient mode'
    ],
    [
        'Shelf Buttressing Back-Pressure Tensor',
        'theta_buttress / sigma_back',
        'Dynamic restraint exerted by floating ice shelf on grounded ice outlet',
        'Spatially varying 2D tensor along grounding line contour (0.0 = collapsed, 1.0 = fully unconfined/intact)',
        'theta in [0.0, 1.0]',
        'Ice shelf geometry, thickness, and pin-point contact observations from BedMachine/MEaSUREs',
        'Identifiable for intact shelves (Larsen C, George VI); zero for collapsed shelves (Larsen A, B)',
        'Confounded with form drag and narrow fjord pinning',
        'Prescribe explicitly based on documented collapse history (Larsen A = 0.0 post-1995; Larsen B = 0.0 post-2002; Larsen C = 1.0 intact)'
    ]
]

p_iden = os.path.join(repo_tables, 'phase5_stage4_parameter_identifiability_plan.csv')
with open(p_iden, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(iden_headers)
    w.writerows(iden_rows)
shutil.copy2(p_iden, os.path.join(brain_tables, 'phase5_stage4_parameter_identifiability_plan.csv'))

# 5. Numerical Verification Strategy
verif_headers = [
    'Verification_Module_ID',
    'Target_Numerical_Component',
    'Governing_Numerical_Scheme',
    'Convergence_and_Stopping_Criteria',
    'Residual_Normalization_Formula',
    'Adaptive_Timestepping_and_Rollback_Rule',
    'Mass_Conservation_Verification_Metric',
    'Momentum_Convergence_Verification_Metric',
    'Benchmark_Test_Suite',
    'Acceptance_Threshold'
]

verif_rows = [
    [
        'VERIF_SSA_2D',
        '2D SSA Non-linear Momentum Solver',
        'Preconditioned Inexact Newton-Krylov (PIN-K) with GMRES linear solver and algebraic multigrid (AMG) preconditioner',
        'Non-linear relative residual ||F(u)||_2 / ||F(u_0)||_2 <= 1.0e-05 OR absolute residual <= 1.0e-04 m/yr',
        'res = ||u^(k+1) - u^(k)||_2 / (||u^(k)||_2 + u_scale * sqrt(N_active)) with u_scale = 100 m/yr',
        'Backtracking line-search with Armijo condition; if line-search fails, reduce timestep dt = dt / 2 and rollback state',
        'N/A (Momentum solve preserves mass implicitly via fixed geometry during Picard/Newton step)',
        'Momentum equilibrium residual norm ||div(sigma) - tau_b - rho g H grad(s)||_inf <= 1.0e-03 kPa',
        'ISMIP-HOM Experiment A & C (Higher-order and SSA benchmark over undulating bed)',
        'Relative error <= 1.5% against analytical and community consensus solutions'
    ],
    [
        'VERIF_CONT_2D',
        '2D Finite-Volume Ice Continuity Solver',
        'High-resolution multi-dimensional flux-limiting finite volume scheme (2D TVD-Superbee / MC limiter)',
        'Courant-Friedrichs-Lewy (CFL) stability criterion: dt <= 0.4 * min(dx / |u|, dy / |v|)',
        'CFL = max(|u|/dx + |v|/dy) * dt <= 0.5',
        'Adaptive CFL-based timestepping: dt_new = min(dt_max, 0.4 / CFL_max); automatic rollback if CFL > 0.8',
        'Discrete domain mass balance: |Delta M_grounded - (M_SMB - M_GL + M_remap)| / M_init <= 1.0e-14',
        'N/A (Continuity step operates on converged velocity field)',
        '2D Time-dependent cone transport benchmark & deforming Gaussian pulse advection',
        'Machine precision conservation (|res| <= 1.0e-12 relative error); zero spurious negative thicknesses'
    ],
    [
        'VERIF_GL_2D',
        '2D Grounding-Line Migration & Contact Problem',
        'Sub-grid linear interpolation of flotation condition rho_i H = -rho_w b across 2D cell edges with SEP3 flux boundary condition',
        'Grounding line position stability: delta x_GL / dx <= 1.0e-03 between successive Picard iterations',
        'Flotation residual: Delta H_float = H - (-rho_w/rho_i * b); sign transition tracked across cell boundaries',
        'If grounding line jumps > 2 cells in a single step, reduce dt = dt / 4 and recalculate contact state',
        'Boundary mass transfer: Delta M_boundary strictly bookkept into floating ledger; relative error <= 1.0e-14',
        'Transverse grounding-line stress continuity [[sigma_nn]] = 0 across floating cavity transition',
        'MISMIP+ Benchmark (Marine Ice Sheet Model Intercomparison Project Plus: Experiments ice0, ice1r, ice1ra)',
        'Grounding line steady-state position matches MISMIP+ ensemble median within 0.5 grid cells'
    ],
    [
        'VERIF_INTEG_AP',
        'Full Domain A Coupled Verification',
        'Fully coupled 2D SSA + 2D FV Continuity + RACMO2.3p2 SMB across all 866,358 cells of Domain A',
        'Simultaneous convergence of momentum (res <= 1.0e-4) and continuity (CFL <= 0.5) at all 250 forward steps',
        'Coupled norm: res_coupled = max(res_momentum, res_CFL)',
        'Automatic checkpointing at each 0.25-yr interval; automatic retry with dt_sub = dt / 2 on solver stagnation',
        'Domain-wide discrete mass residual <= 10.0 kg over 5-year simulation (< 1.0e-14 relative error)',
        'Zero unconverged momentum states accepted across all timesteps (100% convergence enforcement)',
        'Historical 1996-2016 Antarctic Peninsula hindcast (5-year diagnostic verification)',
        '100% convergence rate, machine precision mass conservation, zero unmodeled remainder cells'
    ]
]

p_verif = os.path.join(repo_tables, 'phase5_stage4_numerical_verification_strategy.csv')
with open(p_verif, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(verif_headers)
    w.writerows(verif_rows)
shutil.copy2(p_verif, os.path.join(brain_tables, 'phase5_stage4_numerical_verification_strategy.csv'))

print("All Stage 4.0 architecture design tables successfully generated and mirrored.")

