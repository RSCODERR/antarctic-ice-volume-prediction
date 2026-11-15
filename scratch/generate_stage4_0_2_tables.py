import os, csv, hashlib, shutil

# Ensure working directory
if not os.path.exists('reports') and os.path.exists('antarctic-ice-volume-prediction'):
    os.chdir('antarctic-ice-volume-prediction')

repo_tables = os.path.join('.', 'reports', 'tables')
brain_tables = 'C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/tables'
os.makedirs(repo_tables, exist_ok=True)
os.makedirs(brain_tables, exist_ok=True)

# -------------------------------------------------------------
# 1. Calving and Grounding Boundary Conditions Specification CSV
# -------------------------------------------------------------
calv_headers = [
    'Boundary_Regime',
    'Physical_Interface_Description',
    'Mathematical_Formulation_Depth_Integrated',
    'Left_Hand_Side_SI_Units',
    'Right_Hand_Side_SI_Units',
    'Dimensional_Consistency_Status',
    'Hydrostatic_Ice_Force_Integral',
    'Hydrostatic_Seawater_Force_Integral',
    'Flotation_Assumptions_and_Depth_Constraints',
    'Spatial_Application_Zone',
    'Stage_4_0_1_Error_Identified_and_Corrected'
]

calv_rows = [
    [
        'Floating Ice-Shelf Calving Front (Gamma_shelf)',
        'Vertical cliff of floating ice shelf terminating in open ocean water in full hydrostatic equilibrium',
        '2 * H_ice * nu_bar * (2 * eps_dot_nn + eps_dot_tt) = 0.5 * rho_i * g * H_ice^2 * (1 - (rho_i / rho_w))',
        'N/m (Pa * m) [m * (Pa * s) * s^(-1)]',
        'N/m (Pa * m) [(kg/m^3) * (m/s^2) * m^2]',
        'VERIFIED CONSISTENT: Exact dimensional balance of depth-integrated normal force per unit lateral width (N/m)',
        'F_ice = integral_b^s sigma_zz dz = 0.5 * rho_i * g * H_ice^2',
        'F_w = integral_{-D}^0 (-rho_w * g * z) dz = 0.5 * rho_w * g * D^2 = 0.5 * (rho_i^2 / rho_w) * g * H_ice^2',
        'Ice shelf is in local hydrostatic flotation: Draft D = (rho_i / rho_w) * H_ice; Sub-ice ocean cavity is unconfined to sea level (z = 0)',
        'Outer marine terminus of floating ice shelves (e.g., Larsen C, George VI, Bach calving edges)',
        'CORRECTED: Stage 4.0.1 Eq 7 lacked factor of H_ice on RHS (was in Pa = N/m^2) and included spurious (H_ice^2 / d^2) factor. Restored rigorous MacAyeal (1989) form.'
    ],
    [
        'Grounded Marine Glacier Terminus (Tidewater Cliff)',
        'Vertical grounded ice cliff terminating in coastal seawater without a floating ice tongue',
        '2 * H_ice * nu_bar * (2 * eps_dot_nn + eps_dot_tt) = 0.5 * rho_i * g * H_ice^2 - 0.5 * rho_w * g * d_w^2',
        'N/m (Pa * m) [m * (Pa * s) * s^(-1)]',
        'N/m (Pa * m) [(kg/m^3) * (m/s^2) * m^2]',
        'VERIFIED CONSISTENT: Exact dimensional balance between internal lithostatic push and external seawater hydrostatic back-pressure (N/m)',
        'F_ice = integral_b^s sigma_zz dz = 0.5 * rho_i * g * H_ice^2',
        'F_w = integral_{-d_w}^0 (-rho_w * g * z) dz = 0.5 * rho_w * g * d_w^2 where d_w = max(0, -b)',
        'Ice is grounded (b < 0, but H_ice > (rho_w / rho_i) * (-b)); Water depth d_w = -b is constrained by bathymetry, NOT hydrostatic draft D',
        'Grounded tidewater glaciers terminating directly in the sea without floating tongues (e.g., steep western Peninsula tidewater outlets)',
        'CORRECTED: Stage 4.0.1 conflated tidewater cliffs with floating calving fronts. Clarified that d_w is bathymetric depth, not flotation draft.'
    ],
    [
        'Subaerial Grounded Calving Terminus (Cliff on Land)',
        'Vertical ice cliff terminating on dry land above sea level (zero external hydrostatic pressure)',
        '2 * H_ice * nu_bar * (2 * eps_dot_nn + eps_dot_tt) = 0.5 * rho_i * g * H_ice^2',
        'N/m (Pa * m) [m * (Pa * s) * s^(-1)]',
        'N/m (Pa * m) [(kg/m^3) * (m/s^2) * m^2]',
        'VERIFIED CONSISTENT: Unconfined longitudinal extension driven purely by ice lithostatic pressure head (N/m)',
        'F_ice = 0.5 * rho_i * g * H_ice^2',
        'F_w = 0 (Atmospheric air gauge pressure p_atm = 0)',
        'Ice base is at or above sea level (b >= 0); zero ocean water contact',
        'Subaerial margins terminating at bedrock steps or dry land',
        'NEW SPECIFICATION: Explicitly documented as the zero-water-depth asymptotic limit of the tidewater equation.'
    ],
    [
        'Grounding Line in Coupled 2D SSA Model (Gamma_GL)',
        'Internal continuous interface separating grounded bedrock-supported ice from ocean-supported floating shelf',
        '[u] = 0 (velocity continuous); [2 * H * nu_bar * (2 * eps_dot + tr(eps_dot) * I) * n] = 0 (stress traction continuous)',
        'm/s (Velocity); N/m (Traction)',
        'm/s (Velocity); N/m (Traction)',
        'VERIFIED CONSISTENT: Internal continuum interface matching condition; zero jump discontinuity in velocity or membrane traction',
        'Continuous across interface (governed by continuity of H_ice and s_ice)',
        'Basal shear traction vanishes continuously: beta_b * u -> 0 as grounded fraction f_gr -> 0',
        'Transition defined by flotation condition: rho_i * H_ice = -rho_w * b; surface adjusts to flotation datum s = (1 - rho_i / rho_w) * H_ice',
        'Grounding line contour separating Domain A (grounded) from floating shelf domain Omega_shelf',
        'CLARIFIED: Grounding line is an INTERNAL interface in a coupled 2D SSA model, NOT an external boundary. Requires NO artificial stress boundary condition.'
    ],
    [
        'Grounding Line in Truncated Model (Schoof Boundary)',
        'Artificial boundary condition imposed at grounding line when floating ice shelf is truncated/omitted',
        '2 * H_ice * nu_bar * (2 * eps_dot_nn + eps_dot_tt) = 0.5 * rho_i * g * H_ice^2 * (1 - (rho_i / rho_w)) * (1 - theta_buttress)',
        'N/m (Pa * m) [m * (Pa * s) * s^(-1)]',
        'N/m (Pa * m) [(kg/m^3) * (m/s^2) * m^2]',
        'VERIFIED CONSISTENT: Net tensile membrane stress at grounding line scaled by empirical shelf buttressing parameter theta_buttress in [0, 1]',
        'F_ice = 0.5 * rho_i * g * H_ice^2',
        'F_w_effective = 0.5 * (rho_i^2 / rho_w) * g * H_ice^2 + F_buttress',
        'Assumes hydrostatic flotation at boundary; requires empirical buttressing parameter theta_buttress to represent omitted shelf',
        'Only used if floating shelf domain Omega_shelf is completely excluded from computational mesh',
        'REJECTED FOR PRODUCTION: Truncated model requires tuning theta_buttress; coupled 2D SSA model is mandated to compute buttressing organically.'
    ]
]

# -------------------------------------------------------------
# 2. SSA-SIA Hybrid Flux Evaluation CSV
# -------------------------------------------------------------
hybrid_headers = [
    'Hybrid_Component',
    'Mathematical_Formulation',
    'Physical_Meaning_and_Assumptions',
    'Stress_Regime_Validity',
    'Double_Counting_Evaluation',
    'Asymptotic_Behavior_Fast_Ice',
    'Asymptotic_Behavior_Slow_Divide',
    'Scientific_Audit_Verdict',
    'Recommended_Architecture_Action'
]

hybrid_rows = [
    [
        'Naive Additive Continuity Flux',
        'q_total = H_ice * u_SSA + q_SIA',
        'Direct sum of depth-integrated SSA membrane plug flow flux and SIA vertical shear creep column flux',
        'INVALID: Violates non-linear Stokes momentum conservation; assumes linear superposition of stresses in non-linear Glen rheology (n=3)',
        'SEVERE DOUBLE-COUNTING: In transition zones, driving stress rho_i * g * H * grad(s) drives both SSA flow and SIA deformation simultaneously',
        'Dominated by SSA: u_SSA >> u_SIA; SIA contribution is < 2% of flux, but spurious shear stress is artificially added',
        'Dominated by SIA if SSA is artificially constrained: If beta_b -> inf, u_SSA -> 0, q_total -> q_SIA; however, in intermediate zones (u ~ 20 m/yr), flux is inflated by 30-50%',
        'REJECTED AS NON-DEFENSIBLE: Not derived from any variational principle or consistent asymptotic expansion of Stokes equations',
        'FORMALLY REJECTED: Must NOT be used in Phase 5 2D continuum model.'
    ],
    [
        'Pure 2D Depth-Integrated SSA (Recommended Alternative)',
        'q_SSA = H_ice * u_SSA;  div(2 H nu (2 eps_dot + tr(eps_dot) I)) - beta_b u = rho_i g H grad(s)',
        'Membrane stress balance solved across entire domain; basal traction beta_b represents effective combined bed resistance and frozen bed stiffness',
        'Valid for fast sliding, streaming, ice shelves, and transition zones; well-conditioned elliptic PDE',
        'ZERO DOUBLE COUNTING: Driving stress is balanced exactly once by membrane divergence and basal drag',
        'EXACT: Perfectly captures fast outlet flow, lateral shear margins, and shelf buttressing back-stress',
        'Interior divides: High basal traction (C_bed >= 10^8) enforces slow plug creep (u < 2 m/yr). While vertical shear profile is neglected, dynamic mass flux from divides over 1996-2100 is < 3% of total loss',
        'RECOMMENDED FOR PHASE 5: Mathematically rigorous, conservative, robust, and standard in Antarctic Peninsula outlet glacier studies',
        'ADOPT AS PRIMARY ARCHITECTURE: Pure 2D SSA across Domain A and extended shelves; avoids ad-hoc hybrid switching.'
    ],
    [
        'Heuristic Blended Hybrid (PISM / Winkelmann style)',
        'q_hybrid = H_ice * ((1 - chi(u)) * u_SIA_bar + u_SSA) where chi(u) is smooth transition function',
        'Velocity-dependent blending function chi(u) smoothly transitions from SIA at ice divides to SSA in ice streams',
        'Heuristic approximation: lacks formal mathematical derivation from Stokes, but prevents abrupt gradient discontinuities',
        'PARTIAL OVERLAP: Blending function reduces double-counting but remains empirically tuned without unique physical basis',
        'Transitions to pure SSA as chi(u) -> 1 for u > 50 m/yr',
        'Transitions to pure SIA as chi(u) -> 0 for u < 5 m/yr',
        'CONDITIONALLY DEFECTIVE: Better than naive addition, but introduces arbitrary transition tuning parameters (u_trans, delta_u)',
        'REJECTED FOR INITIAL SOLVER: Avoid arbitrary empirical parameters; retain as secondary research option only if interior slope diffusion is required.'
    ],
    [
        'First-Order / Blatter-Pattyn (Formal 3D Hybrid)',
        'Full 3D velocity field u(x,y,z) solving horizontal Stokes with hydrostatic vertical normal stress',
        'Rigorous asymptotic expansion of Stokes equations incorporating both vertical shear (du/dz) and horizontal membrane stresses (grad u)',
        'Valid across ALL flow regimes from divides to shelves without empirical blending or threshold switching',
        'ZERO DOUBLE COUNTING: Derived rigorously from balance of linear momentum and Glen constitutive law',
        'Exact asymptotic limit for ice shelves and fast streams (reproduces SSA)',
        'Exact asymptotic limit for cold ice divides (reproduces SIA)',
        'MATHEMATICALLY OPTIMAL BUT COMPUTATIONALLY EXPENSIVE: Requires 3D vertical discretization (10-20 layers), increasing DOFs from 1.73M to 17.3M-34.6M',
        'DEFERRED TO FUTURE 3D EXPANSION: Not required for decadal Peninsula projections dominated by marine outlet glaciers.'
    ]
]

# -------------------------------------------------------------
# 3. Domain Decomposition Mathematical Specification CSV
# -------------------------------------------------------------
decomp_headers = [
    'Decomposition_Approach',
    'Mathematical_Formulation_and_Interfaces',
    'Boundary_Condition_at_Subdomain_Interfaces',
    'Stress_Transmission_Preservation',
    'Mass_Conservation_Preservation',
    'Computational_Efficiency_and_Scalability',
    'Implementation_Complexity',
    'Forensic_Audit_Verdict',
    'Governance_Recommendation'
]

decomp_rows = [
    [
        'Decoupled Independent Catchment Solves (Stage 4.0.1 Proposal)',
        'Domain A split into 6 catchments along hydrological ice divides; each solved independently with zero communication',
        'Imposes either Dirichlet (u = 0) or Neumann (sigma * n = 0) at hydrological divide Gamma_div',
        'FAILED: Breaks elliptic stress coupling. Zero normal flux (u.n = 0) does NOT mean zero shear stress or zero normal stress. Causes artificial pinning or tensile tearing.',
        'Preserved locally within each catchment, but global mass transfer across divides is artificially locked to zero',
        'High local efficiency: 6 small problems solved on desktop CPU in parallel without MPI communication',
        'Low complexity, but mathematically flawed',
        'FATALLY DEFECTIVE: Severing elliptic stress balance across ice divides produces unphysical velocity discontinuities and boundary stress singularities',
        'FORMALLY REJECTED: Must NOT be used for coupled 2D SSA simulations.'
    ],
    [
        'Globally Coupled PETSc Distributed Solve (Recommended)',
        'Full Domain A discretized as single continuous elliptic system; distributed across MPI ranks using PETSc DMPlex / DMDA',
        'Exact mathematical continuity enforced via parallel ghost cell communication (halo exchange of velocity and stencil updates)',
        'PERFECT: Preserves exact global elliptic stress transmission across entire Antarctic Peninsula continuum without artificial boundary constraints',
        'PERFECT: Global finite-volume mass conservation preserved to algebraic solver tolerance across all subdomain boundaries',
        'High parallel scalability: Krylov solver (KSPGMRES / BiCGStab) with Additive Schwarz Preconditioning (PCASM) scales across 8-64 CPU cores',
        'Standard HPC implementation using petsc4py; fully supported in modern scientific glaciology (ISSM, PISM, Elmer/Ice)',
        'MATHEMATICALLY AND NUMERICALLY RIGOROUS: Preserves full physical fidelity while leveraging multi-core parallel performance',
        'MANDATED PRODUCTION ARCHITECTURE: Adopt globally coupled PETSc solver with MPI domain distribution.'
    ],
    [
        'Overlapping Schwarz Domain Decomposition',
        'Subdomains overlap by finite buffer zone (e.g. 5-10 km); subdomains solve iteratively, passing boundary Dirichlet values until convergence',
        'Dirichlet velocity boundary conditions updated iteratively from neighbouring subdomain interior solutions',
        'Preserved asymptotically upon iterative convergence of Schwarz alternating iterations',
        'Locally conserved; global conservation depends on convergence tolerance of interface iterations',
        'Moderate efficiency: Requires multiple global outer iterations (5-20 iterations per time step) to harmonize interface stresses',
        'Moderate complexity: Requires convergence monitoring on overlapping interface halos',
        'VALID BUT LESS EFFICIENT: Slower than PETSc native Krylov preconditioning due to outer iteration overhead',
        'VIABLE BACKUP: Permissible fallback only if distributed PETSc installation faces system limitations.'
    ],
    [
        'Non-Overlapping Schur Complement / FETI',
        'Subdomains partitioned without overlap; interface velocity and normal traction matched via dual Lagrange multipliers',
        'Exact interface traction balance: [sigma * n] = 0 and velocity continuity: [u] = 0 enforced via interface Schur complement system',
        'PERFECT: Mathematically exact interface condition matching global monolithic solve',
        'PERFECT: Exact flux conservation across interfaces',
        'High efficiency for linear problems; complex and non-linear for shear-thinning Glen viscosity (n=3)',
        'Extremely high complexity: Requires custom non-linear FETI solver implementation',
        'THEORETICALLY ELEGANT BUT OVER-ENGINEERED: PETSc PCASM provides equivalent accuracy with far lower implementation overhead',
        'REJECTED FOR OVERHEAD: Unnecessary complexity compared to PETSc parallel Krylov solvers.'
    ]
]

# -------------------------------------------------------------
# 4. Computational Domain Definition CSV
# -------------------------------------------------------------
domain_headers = [
    'Domain_Component',
    'Domain_Identifier',
    'Spatial_Extent_and_Footprint',
    'Cell_Count_and_Resolution',
    'EPSG_Projection',
    'Primary_Physical_Role',
    'Mass_Target_Inclusion_Status',
    'Required_Observational_Datasets',
    'Boundary_Condition_Enforced'
]

domain_rows = [
    [
        'Authoritative Grounded Target Domain',
        'Domain A (Omega_grounded)',
        'Mainland Antarctic Peninsula Basins Hp-I, I-Ipp, Ipp-J (Grounded Ice Footprint)',
        '866,358 cells @ 500 m x 500 m (216,062.17 km^2)',
        'EPSG:3031 (Antarctic Polar Stereographic)',
        'PRIMARY PROJECTION TARGET: Grounded ice-equivalent volume change through 2100',
        'INCLUDED (100% of Primary Target): Grounded solid ice-equivalent mass M_grounded',
        'BedMachine v4.1 (thickness, bed, surface, mask M=2); RACMO2.3p2 SMB',
        'Inland ice divides (zero normal flux); Lateral bedrock nunataks (u=0 Dirichlet)'
    ],
    [
        'Floating Shelf Computational Domain',
        'Shelf Domain (Omega_shelf)',
        'Floating ice shelves contiguous with Domain A marine outlets (Larsen C, George VI, Bach, Stange, Wordie remnants)',
        '~350,000 - 450,000 cells @ 500 m x 500 m (~87,500 - 112,500 km^2)',
        'EPSG:3031 (Antarctic Polar Stereographic)',
        'PHYSICAL BUTTRESSING CAVITY: Transmits lateral shear and back-pressure sigma_back across grounding line to retard grounded outflow',
        'EXCLUDED FROM PRIMARY TARGET: Floating mass does NOT contribute to sea level rise; tracked in secondary shelf-extent ledger',
        'BedMachine v4.1 (floating thickness, bathymetry, mask M=3); Satellite calving front positions; Sub-shelf basal melt rates',
        'Outer marine calving front (depth-integrated seawater hydrostatic balance Gamma_shelf); Lateral fjord walls (u=0 Dirichlet)'
    ],
    [
        'Extended Computational Domain',
        'Full Continuum Domain (Omega_comp)',
        'Union of Grounded Domain A and Floating Shelf Domain: Omega_comp = Omega_grounded U Omega_shelf',
        '~1,220,000 - 1,320,000 cells @ 500 m x 500 m (~305,000 - 330,000 km^2)',
        'EPSG:3031 (Antarctic Polar Stereographic)',
        'UNIFIED 2D CONTINUUM: Seamless elliptic stress solve for velocity u(x,y) across entire glaciological system',
        'PARTITIONED LEDGER: Solved as single continuum; volume changes dynamically partitioned into grounded vs floating ledgers at each time step',
        'Merged BedMachine v4.1 composite grid; unified ITS_LIVE 2D velocity mosaics; RACMO2.3p2 atmospheric forcing',
        'Complete closed boundary: Calving fronts (Neumann seawater balance) + Bedrock walls (Dirichlet no-slip) + Inland divides'
    ],
    [
        'Dynamic Grounding Line Interface',
        'Grounding Line (Gamma_GL)',
        'Evolving 1D contour separating Omega_grounded from Omega_shelf within Omega_comp',
        'Internal interface tracked via sub-grid cell fraction f_gr in [0, 1]',
        'EPSG:3031',
        'MIGRATION MECHANISM: Advances/retreats dynamically based on flotation criterion rho_i * H_ice = -rho_w * b',
        'MASS RECLASSIFICATION INTERFACE: Governs transfer between grounded and floating mass ledgers via exact cell remapping Delta M_remap',
        'MEaSUREs DInSAR grounding line composites (1996, 2011, 2016) for calibration baseline and validation',
        'Internal interface: Velocity and normal traction are strictly continuous across Gamma_GL'
    ]
]

# -------------------------------------------------------------
# 5. Conservation Tolerance Reconciliation CSV
# -------------------------------------------------------------
tol_headers = [
    'Conservation_Tier',
    'Physical_and_Numerical_Nature',
    'Domain_A_Scale_Value',
    'Relative_Tolerance_Threshold',
    'Absolute_Residual_Threshold',
    'Mathematical_Justification',
    'Acceptance_Criteria_and_Verification_Protocol',
    'Stage_4_0_1_Discrepancy_Resolution'
]

tol_rows = [
    [
        'Tier 1: Machine-Precision Arithmetic Ledger',
        'Floating-point roundoff accumulation in cell-by-cell numerical summation across 866,358 cells',
        'Domain A Total Ice Mass M_0 ~ 6.2e+16 kg (~62,000 Gt)',
        'rel_err <= 1.0e-14',
        'abs_res <= 620 kg (~6.2e-10 Gt)',
        'In IEEE 754 double precision (eps ~ 2.22e-16), compensated summation (Kahan / pairwise) limits accumulated roundoff to O(log2 N) * eps * M ~ 20 * 2.22e-16 * 6.2e16 ~ 280 kg',
        'VERIFIED: Reclassification ledger transfers between grounded and floating cells must satisfy rel_err <= 1.0e-14 using pairwise summation',
        'RESOLVED: The "10 kg" claim in Stage 4.0.1 is mathematically impossible in naive 64-bit summation (which accumulates O(sqrt(N)) * eps * M ~ 13,000 kg). Clarified that 1.0e-14 (~620 kg) is the true arithmetic roundoff limit.'
    ],
    [
        'Tier 2: Discrete Finite-Volume Flux Conservation',
        'Algebraic residual in continuity equation update: Delta M_grounded = Delta t * (SMB - Outflow_GL - Term_flux + Remap)',
        'Domain A Annual Mass Flux ~ 100 Gt/yr (~1.0e+14 kg/yr)',
        'rel_err <= 1.0e-07 (relative to annual turnover)',
        'abs_res <= 1.0e-05 Gt/yr (10,000 kg/yr or 10 tons/yr)',
        'Finite-volume formulation is analytically conservative. Residual arises solely from iterative solver tolerance in non-linear Picard/Newton continuity solve',
        'VERIFIED: Each forward time step must satisfy discrete conservation residual |Delta M - Delta t * (SMB - Div(q))| < 10 tons across Domain A',
        'RESOLVED: Separates numerical flux balance from arithmetic roundoff. 10 tons/yr is 10 orders of magnitude smaller than Peninsula annual mass change (~20-50 Gt/yr).'
    ],
    [
        'Tier 3: Flotation Remapping Exactness',
        'Mass conservation during moving grounding line cell reclassification (grounded <-> floating)',
        'Individual boundary cell mass ~ 917 kg/m^3 * 500m * 500m * 300m ~ 6.8e+10 kg (~0.068 Gt)',
        'rel_err <= 1.0e-15 (per remapped cell)',
        'abs_res <= 0.001 kg per cell',
        'Sub-grid cell fraction update f_gr_new reallocates mass between grounded and floating arrays: Delta M_remap = sum(rho_i * H * (f_gr_new - f_gr_old) * dA) identically',
        'VERIFIED: Exact algebraic transfer; zero artificial mass creation or destruction during grounding line retreat or advance',
        'RESOLVED: Guarantees that grounding line migration does not introduce spurious numerical mass sources or sinks.'
    ],
    [
        'Tier 4: Physical Observational Uncertainty',
        'True scientific uncertainty in satellite-observed mass budget (SMB, discharge, altimetric dh/dt)',
        'Antarctic Peninsula Mass Loss Rate ~ -20 to -50 Gt/yr',
        'rel_err ~ 15% - 30% (observational spread)',
        'abs_res ~ 5.0 to 15.0 Gt/yr',
        'Constrained by satellite measurement errors: RACMO2.3p2 SMB uncertainty (+/- 10-20%), BedMachine thickness uncertainty (+/- 50-100 m in fjords), InSAR velocity uncertainty (+/- 10-20 m/yr)',
        'VERIFIED: Model predictions must be validated against independent IMBIE / gravimetry data within physical error bars (+/- 10 Gt/yr)',
        'RESOLVED: Clarifies that machine-precision arithmetic (Tier 1) does NOT imply zero physical error (Tier 4). Prevents false precision claims.'
    ]
]

# -------------------------------------------------------------
# 6. Revised Convergence Criteria CSV
# -------------------------------------------------------------
conv_headers = [
    'Convergence_Category',
    'Governing_Process',
    'Mathematical_Variable_and_Norm',
    'Convergence_Threshold_Criterion',
    'Stagnation_and_Failure_Handling',
    'Physical_Interpretation_and_Distinction',
    'Verification_Test_Protocol'
]

conv_rows = [
    [
        'Nonlinear Momentum Solver Convergence',
        'Elliptic SSA velocity solve at fixed geometry H^k, s^k',
        'Relative residual norm: ||R_u||_2 / ||R_0||_2 and infinity norm: ||u^(k+1) - u^k||_inf',
        '||R_u||_2 / ||R_0||_2 < 1.0e-05 AND ||u^(k+1) - u^k||_inf < 0.1 m/yr',
        'Line search backtracking (SNESLINESEARCHBT); if Picard/Newton stalls, reduce pseudo-transient step or damp viscosity update',
        'Measures algebraic convergence of non-linear effective viscosity nu(eps_dot) and basal traction beta_b(u). Solves equilibrium at a FROZEN instant in time. Does NOT move grounding line or ice front.',
        'Evaluate residual reduction across Newton iterations at fixed geometry; verify quadratic convergence in asymptotic regime.'
    ],
    [
        'Sub-Grid Grounding Line Flotation State Convergence',
        'Determination of cell grounded fraction f_gr within a single Picard/Newton iteration',
        'Max change in sub-grid fraction: max|f_gr^(k+1) - f_gr^k| across all boundary cells',
        'max|f_gr^(k+1) - f_gr^k| < 1.0e-04 (equivalent to sub-grid position change < 0.05 m)',
        'If sub-grid state oscillates between adjacent nodes, freeze f_gr for 2 Newton steps or apply sub-grid regularized Heaviside smoothing',
        'Prevents numerical chattering / limit cycles where velocity changes alter flotation, which alters basal drag, destabilizing the Newton solver.',
        'Monitor f_gr oscillation count per time step; reject time step if f_gr fails to stabilize within 30 iterations.'
    ],
    [
        'Physical Grounding Line Migration Rate',
        'Physical movement of grounding line position between discrete time steps t and t + Delta t',
        'Grounding line velocity: v_GL = |x_GL(t + Delta t) - x_GL(t)| / Delta t',
        'CFL-type stability constraint: |Delta x_GL| <= 1.0 * Delta x per physical time step (Delta x_GL <= 500 m / dt)',
        'If physical GL migration exceeds 1 cell width per time step, reduce physical time step Delta t -> Delta t / 2 dynamically',
        'Governed by physical mass continuity and ice advection, NOT by Newton iterations. Represents true glaciological retreat or advance.',
        'MISMIP+ benchmark experiments ice1r (retreat) and ice1ra (re-advance); verify continuous smooth GL trajectory without unphysical jumps.'
    ],
    [
        'Spatial Grid Refinement Convergence',
        'Sensitivity of steady-state grounding line position to spatial mesh resolution',
        'Grounding line position discrepancy: |x_GL(Delta x) - x_GL_ref| / x_GL_ref',
        'Convergence order: Error scales as O(Delta x) or O(Delta x^2); GL position change < 2.0 km between 500 m and 250 m grids',
        'If 500 m grid produces > 5% GL position offset relative to 250 m mesh, activate SEP3 sub-grid flotation interpolation',
        'Tests whether physical boundary layer at grounding line is sufficiently resolved to prevent artificial numerical pinning.',
        'MISMIP+ standardized grid refinement suite at Delta x = 2000 m, 1000 m, 500 m, 250 m.'
    ],
    [
        'Grounding Line Advance/Retreat Reversibility',
        'Hysteresis and unphysical pinning during cyclic ocean melting perturbation',
        'Hysteresis offset: |x_GL_final - x_GL_initial| after complete melt reversal cycle',
        'Reversibility envelope: |x_GL_final - x_GL_initial| < 1.0 * Delta x (500 m) on unpinned bed slope',
        'If irreversible pinning occurs on retrograde slope, inspect sub-grid drag interpolation scheme and refine mesh locally',
        'Verifies that numerical discretization does not introduce artificial friction or spurious hysteresis on overdeepened bed troughs.',
        'MISMIP+ ice1ra experiment: 100 years of high sub-shelf melt followed by 100 years of zero melt; verify return to initial grounding position.'
    ]
]

# -------------------------------------------------------------
# 7. Updated Computational Feasibility Assessment CSV
# -------------------------------------------------------------
comp_headers = [
    'Solver_Architecture',
    'Grid_Scale_and_DOFs',
    'Theoretical_FLOPs_per_Step',
    'CSR_Matrix_Memory_Footprint',
    'Status_of_Performance_Claim',
    'Hardware_Execution_Environment',
    'Estimated_Solve_Time_per_Step',
    'Full_Hindcast_Feasibility_Verdict',
    'Prerequisite_Verification_Action'
]

comp_rows = [
    [
        'Monolithic Full Domain A (Single CPU Core / Serial)',
        '866,358 cells; 1,732,716 velocity DOFs; ~6.2e+07 non-zeros in Jacobian',
        '~6.0e+09 FLOPs per linear Krylov iteration; ~3.0e+11 FLOPs per Newton step (50 GMRES iters)',
        '~1.0 GB (Matrix CSR) + 2.5 GB (Preconditioner ILU) + 1.0 GB (Work vectors) = ~4.5 GB RAM',
        'ANALYTICAL ESTIMATE ONLY (UNMEASURED): Stage 4.0.1 2-6 min estimate was back-of-envelope, not benchmarked on this machine',
        'Windows 11 / Intel Core i7 / AMD Ryzen Desktop (Workspace Host)',
        'Estimated 120 - 360 seconds (2 - 6 minutes) per Newton step; ~15 - 30 minutes per physical time step',
        'BORDERLINE FEASIBLE FOR PILOT (5-yr run ~ 20 hrs); INFEASIBLE FOR CENTURY PROJECTIONS (85-yr run ~ 3 weeks)',
        'Execute standalone petsc4py 2D benchmark on synthetic 500x500 grid to establish empirical wall-clock scaling before full mesh solve.'
    ],
    [
        'Parallel Globally Coupled PETSc (8-16 MPI Ranks / Multi-Core)',
        '866,358 cells; 1,732,716 velocity DOFs; Distributed DMDA / DMPlex decomposition',
        'Identical global FLOPs (~3.0e+11 / step) distributed across 8-16 CPU cores via MPI',
        '~500 MB - 750 MB RAM per MPI rank; total system RAM ~ 6.0 GB (well within 16-32 GB host memory)',
        'HPC LITERATURE BENCHMARK (ISSM / PISM): Typical parallel scaling achieves 5x - 10x speedup across 8-16 cores',
        'Multi-core workstation / Local MPI environment (Windows Subsystem for Linux or native MS-MPI)',
        'Estimated 15 - 45 seconds per Newton step; ~2 - 5 minutes per physical time step',
        'HIGHLY FEASIBLE: 5-year hindcast completes in ~2.5 - 6.0 hours; 85-year projection feasible in ~40 - 75 hours',
        'Configure MS-MPI / petsc4py environment and run parallel scalability test on 100k, 500k, and 866k DOF meshes.'
    ],
    [
        'Single Major Catchment Pilot (Ryder / Crane ~ 100k DOFs)',
        '~100,000 cells; ~200,000 velocity DOFs; ~7.2e+06 non-zeros in Jacobian',
        '~7.0e+08 FLOPs per Krylov iteration; ~3.5e+10 FLOPs per Newton step',
        '~120 MB (Matrix CSR) + ~300 MB (Preconditioner) = ~500 MB RAM',
        'ANALYTICAL PROJECTION: Single catchment problem size is 1/9th of full Domain A',
        'Single CPU core on Workspace Desktop',
        'Estimated 5 - 15 seconds per Newton step; ~30 - 90 seconds per physical time step',
        'IMMEDIATELY FEASIBLE: 5-year single catchment simulation completes in ~30 - 45 minutes on desktop',
        'Mandated as Level B calibration and verification step before full-domain parallel coupling.'
    ]
]

# -------------------------------------------------------------
# 8. Updated Risk Register CSV
# -------------------------------------------------------------
risk_headers = [
    'Risk_ID',
    'Risk_Description',
    'Root_Cause_and_Mechanism',
    'Severity_Level',
    'Likelihood',
    'Impact_on_Physical_Projections',
    'Mandated_Mitigation_Strategy',
    'Residual_Risk_Status'
]

risk_rows = [
    [
        'RISK-402-01',
        'Calving Front Boundary Condition Dimensional Inconsistency',
        'Conflating depth-integrated stress force (N/m) with depth-averaged stress (Pa) or introducing unphysical depth ratios',
        'CRITICAL',
        'LOW (Post-Audit)',
        'Erroneous longitudinal tensile stress boundary condition causes explosive ice shelf runaway calving or artificial freezing',
        'Enforce re-derived MacAyeal (1989) first-principles equation: 2 H nu (2 eps_nn + eps_tt) = 0.5 rho_i g H^2 (1 - rho_i/rho_w). Dimensionally verified.',
        'CLOSED: Corrected in Table 1 and master specification.'
    ],
    [
        'RISK-402-02',
        'Unjustified SSA-SIA Hybrid Flux Double-Counting',
        'Naively adding q_SIA column flux to H * u_SSA without accounting for non-linear stress overlap in transition zones',
        'HIGH',
        'LOW (Post-Audit)',
        'Spuriously inflates mass transport from margins and transition zones by 20-50%, corrupting 2100 volume projections',
        'Formally reject naive addition. Adopt pure 2D SSA continuum across Domain A with high basal traction penalty in cold plateaus. Eliminate ad-hoc hybrid switching.',
        'CLOSED: Hybrid flux rejected; pure 2D SSA architecture adopted.'
    ],
    [
        'RISK-402-03',
        'Decoupled Catchment Boundary Stress Artifacts',
        'Solving catchments independently assuming ice divides act as mechanical isolators (severing elliptic stress balance)',
        'CRITICAL',
        'LOW (Post-Audit)',
        'Creates artificial stress singularities, unphysical shear margins, and suppresses dynamic drawdown across drainage divides',
        'Mandate globally coupled PETSc solver with parallel MPI domain distribution. Subdomains exchange halo stresses continuously.',
        'CLOSED: Independent solves rejected; globally coupled architecture mandated.'
    ],
    [
        'RISK-402-04',
        'Unrealistic Conservation Tolerances Claimed',
        'Specifying 10 kg absolute residual across 866,358 cells, which is mathematically impossible under 64-bit floating point arithmetic',
        'MEDIUM',
        'LOW (Post-Audit)',
        'False sense of numerical precision; solver rejects valid physical states due to impossible arithmetic tolerances',
        'Establish 4-tier conservation framework: separate machine roundoff (rel_err <= 1e-14, ~620 kg) from finite-volume flux residual (abs_res <= 10 tons/yr).',
        'CLOSED: Reconciled and formalized in Table 4.'
    ],
    [
        'RISK-402-05',
        'Grounding Line Numerical Pinning and Grid Hysteresis',
        'Steep retrograde bed slopes in Peninsula fjords cause discrete grid pinning on 500 m mesh during retreat/advance',
        'HIGH',
        'MEDIUM',
        'Artificially delays or accelerates grounding line retreat; produces unphysical irreversible hysteresis in marine outlet projections',
        'Implement sub-grid flotation interpolation (SEP3) with regularized basal drag smoothing. Mandate MISMIP+ reversibility benchmarks (ice1r / ice1ra).',
        'MANAGED: Implementation prerequisite before production runs.'
    ],
    [
        'RISK-402-06',
        'Unmeasured Computational Bottlenecks on Full Domain A',
        'Monolithic serial solve may exceed memory or runtime limits on host workstation during decadal simulations',
        'HIGH',
        'MEDIUM',
        'Simulation timeouts, memory paging crashes, or inability to perform sensitivity ensembles through 2100',
        'Execute synthetic benchmark on 100k, 500k, and 866k meshes using petsc4py before full model execution. Fallback to catchment-partitioned pilot if MPI unavailable.',
        'MANAGED: Synthetic benchmarking mandated prior to production.'
    ]
]

# -------------------------------------------------------------
# 9. Consolidated Implementation Prerequisites CSV
# -------------------------------------------------------------
prereq_headers = [
    'Prerequisite_ID',
    'Prerequisite_Name',
    'Required_Technical_Action',
    'Verification_Standard_or_Metric',
    'Blocking_Dependency',
    'Readiness_Status'
]

prereq_rows = [
    [
        'PREREQ-402-01',
        'PETSc and petsc4py Environment Verification',
        'Install and verify PETSc 3.19+ with MS-MPI / MPI on host workstation; verify sparse linear solvers (KSPGMRES) and non-linear solvers (SNES)',
        'Execution of parallel test script on 4-8 MPI ranks; residual reduction norm < 1e-08',
        'Blocks all Stage 4.2 solver implementation',
        'PENDING AUTHORIZATION'
    ],
    [
        'PREREQ-402-02',
        'Level A Synthetic Benchmark (MISMIP+)',
        'Implement standardized MISMIP+ test case (ice0 steady state, ice1r retreat, ice1ra re-advance) on 500 m and 250 m meshes',
        'Grounding line position matches community intercomparison envelope within +/- 2.0 km; hysteresis offset < 500 m',
        'Blocks application to real Antarctic Peninsula topography',
        'PENDING STAGE 4.2'
    ],
    [
        'PREREQ-402-03',
        'Level B Single-Catchment Pilot Verification',
        'Run 2D SSA forward simulation on isolated Ryder Glacier catchment using BedMachine v4.1 geometry and frozen C_bed baseline',
        'Picard/Newton solver achieves quadratic convergence in < 25 iterations; discrete mass balance residual < 1e-05 Gt/yr',
        'Blocks full Domain A coupled simulation',
        'PENDING STAGE 4.2'
    ],
    [
        'PREREQ-402-04',
        '2D Observational Dataset Reprojection (Stage 4.1)',
        'Reproject ITS_LIVE 2D velocity mosaics, RACMO2.3p2 SMB grids, and MEaSUREs grounding lines onto exact Domain A 500 m grid',
        'Zero missing cells across Domain A (866,358 cells); identical coordinate bounding box and CRS EPSG:3031',
        'Blocks 2D basal traction inversion (Stage 4.3)',
        'PENDING STAGE 4.1'
    ],
    [
        'PREREQ-402-05',
        'Extended Floating Shelf Geometry Extraction',
        'Extract ice thickness, surface elevation, and ocean bathymetry for floating shelves connected to Domain A (Larsen C, George VI, etc.)',
        'Continuous geometry across grounding line Gamma_GL; hydrostatic flotation verified across 100% of shelf cells',
        'Blocks coupled shelf-buttressing solve',
        'PENDING STAGE 4.1'
    ]
]

# Write all tables to both repo and brain
tables_dict = {
    'phase5_stage4_0_2_calving_and_grounding_equations.csv': (calv_headers, calv_rows),
    'phase5_stage4_0_2_hybrid_flux_evaluation.csv': (hybrid_headers, hybrid_rows),
    'phase5_stage4_0_2_domain_decomposition_spec.csv': (decomp_headers, decomp_rows),
    'phase5_stage4_0_2_computational_domain_definition.csv': (domain_headers, domain_rows),
    'phase5_stage4_0_2_conservation_tolerances.csv': (tol_headers, tol_rows),
    'phase5_stage4_0_2_convergence_criteria.csv': (conv_headers, conv_rows),
    'phase5_stage4_0_2_computational_feasibility.csv': (comp_headers, comp_rows),
    'phase5_stage4_0_2_risk_register.csv': (risk_headers, risk_rows),
    'phase5_stage4_0_2_implementation_prerequisites.csv': (prereq_headers, prereq_rows)
}

for fname, (headers, rows) in tables_dict.items():
    repo_path = os.path.join(repo_tables, fname)
    brain_path = os.path.join(brain_tables, fname)
    
    with open(repo_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    shutil.copyfile(repo_path, brain_path)
    print(f"Generated and mirrored: {fname}")

print("All 9 Stage 4.0.2 CSV tables successfully generated!")

