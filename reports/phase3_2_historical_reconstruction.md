# Phase 3.2 Technical Report: Historical Grounded Ice-Equivalent Volume Reconstruction (1979–2024)

**Project:** Antarctic Peninsula Ice-Volume Prediction to 2100  
**Phase:** Phase 3.2 — Historical Grounded Ice-Equivalent Volume Reconstruction  
**Status:** Completed — Trajectories Reconstructed & Validated Against Official IMBIE Benchmark  
**Date:** November 2026  

---

## Executive Summary & Core Results

Phase 3.2 delivers the complete physics-based historical reconstruction of grounded ice-equivalent volume changes across the Antarctic Peninsula mainland basins (`Hp-I`, `I-Ipp`, and `Ipp-J`) from 1979 to 2024. 

In strict adherence to project directives:
- **No machine-learning models have been trained.**
- **No 2100 forecasts have been produced.**
- **No missing observations have been fabricated.**
- **Modelled discharge is never described as observed discharge.**
- **IMBIE 2026 is used strictly as an aggregate regional sector benchmark, never as basin-level ground truth.**
- **Agreement with IMBIE is not claimed as proof that basin-level distributions are correct.**
- **The +7,204.9 km³ Bedmap3–BedMachine discrepancy is preserved as an inter-product structural gap, not a statistical confidence interval.**
- **Bedmap3 and BedMachine baseline realizations are maintained separately without averaging.**

### Primary Numerical Findings (1979–2024):
1. **Central Scenario Reconstructed Grounded Loss (Domain A, $216,062.2\text{ km}^2$):**
   - By December 2023 (IMBIE overlap period): **$-907.69\text{ km}^3$** of solid ice-equivalent volume loss, corresponding to **$-832.35\text{ Gt}$** of grounded ice mass.
   - By December 2024: **$-941.28\text{ km}^3$** ($-863.15\text{ Gt}$).
2. **Official IMBIE-3 Consensus Benchmark Validation (1979–2023):**
   - The reconstructed Central mass loss ($-832.35\text{ Gt}$) agrees with the official Otosaka et al. (2026) IMBIE record (**$-816.97 \pm 108.77\text{ Gt}$**, $1\sigma$) with a residual of only **$-15.38\text{ Gt}$** ($1.9\%$ volume residual, well within $1\sigma$).
   - Across all 45 overlapping years, 34 of 45 years ($75.6\%$) fall within the $1\sigma$ envelope, and **100% of years fall strictly within the $2\sigma$ envelope**.
3. **Basin-Level Dynamic Breakdown (Central Scenario by 2024):**
   - **Basin `Ipp-J` (North Graham Land East / Larsen Embayments):** **$-489.49\text{ km}^3$** ($52.0\%$ of total loss). Dynamic loss surged following the 1995 Larsen A and 2002 Larsen B shelf collapses.
   - **Basin `I-Ipp` (North Graham Land West):** **$-249.89\text{ km}^3$** ($26.5\%$ of total loss), driven by persistent tidewater glacier retreat along Danco and Graham coasts.
   - **Basin `Hp-I` (Palmer Land West):** **$-201.90\text{ km}^3$** ($21.5\%$ of total loss), driven by Wordie Ice Shelf tributary acceleration (1989–1991) while the George VI sector remained stable.
4. **Scenario Divergence Across Epoch 1 (1979–1999):**
   - **Low Scenario (Balance Flux pre-2000):** $-627.48\text{ km}^3$ by 2024 ($-113.72\text{ km}^3$ by 1999).
   - **Central Scenario (InSAR-Calibrated IOM):** $-941.28\text{ km}^3$ by 2024 ($-223.04\text{ km}^3$ by 1999).
   - **High Scenario (Glacier-Specific Acceleration):** $-1,289.42\text{ km}^3$ by 2024 ($-339.45\text{ km}^3$ by 1999).
   - Scenario branches are maintained separately; they are **never averaged**.
5. **Dual Baseline Realizations on Domain A:**
   - **Bedmap3 Domain A Baseline:** $133,497.59\text{ km}^3 \rightarrow \mathbf{132,556.31\text{ km}^3}$ in 2024.
   - **BedMachine V4.1 Domain A Baseline:** $140,702.51\text{ km}^3 \rightarrow \mathbf{139,761.23\text{ km}^3}$ in 2024.
   - **Structural Invariant Offset:** $\mathbf{+7,204.92\text{ km}^3}$ (+5.40%) preserved intact across all years.

---

## 1. Mandatory Preflight Check Resolutions

Prior to running the reconstruction code, all four mandatory preflight checks were rigorously verified and audited against the primary source datasets.

### Table 1.1: Preflight Audit and Reconciliation Master Table

| Preflight Item | Audited Specification | Preflight Status | Physical & Numerical Justification |
| :--- | :--- | :---: | :--- |
| **1. Domain A Cell-Count Discrepancy** | True Count: **866,358 cells** ($216,062.17\text{ km}^2$) | **RESOLVED & RECONCILED** | The 863,979 count in Phase 3.1B text was a clerical artifact of subtracting 22,235 from an unverified draft of 886,214 ($886,214 - 22,235 = 863,979$). The true audited Bedmap3 grounded count is $888,593$. Subtracting the 22,235 Bedmap3-only cells yields exactly **866,358 cells** ($888,593 - 22,235 = 866,358$). All Phase 2.6 rasters, baseline areas ($216,062.17\text{ km}^2$), and volumes ($133,497.59\text{ km}^3$ vs $140,702.51\text{ km}^3$) are 100% consistent with 866,358 cells. Baseline arrays were not altered. |
| **2. IMBIE Cumulative Uncertainty** | Reported Dec 2023: **$\pm 108.7695\text{ Gt}$** | **CONFIRMED 1-SIGMA** | Official metadata comment confirms: *"The respective one sigma uncertainties for each reconciled dataset are provided."* $\pm 108.7695\text{ Gt}$ is already the cumulative $1\sigma$ uncertainty. **Zero additional $\sqrt{12}$ factor was applied.** |
| **3. Regional GIA Implementation** | Nield et al. (2014) Slab Window Viscoelastic Model | **VALIDATED & NON-UNIFORM** | Rejects uniform uplift and rejects Amundsen Sea transfer. Implements spatially varying slab-window model: $+8\text{ to }+15\text{ mm/yr}$ in northern Graham Land (`Ipp-J`), $+4.2\text{ mm/yr}$ in western Graham Land (`I-Ipp`), and $+1.8\text{ mm/yr}$ in southern Palmer Land (`Hp-I`). Verified against UKANET/LARISSA GPS stations. Separates instantaneous elastic rebound ($+2\text{ to }+6\text{ mm/yr}$ near gates) and firn compaction. |
| **4. Units, Signs, and Reference Epochs** | $\text{mm w.e./yr} \rightarrow \text{Gt/yr} \rightarrow \text{km}^3/\text{yr}$ | **VERIFIED** | $\Delta V = \Delta M / 0.917\text{ Gt/km}^3$. Reference epoch: $t_0 = 1979.0$ with $\Delta V(1979.0) = 0.0\text{ km}^3$. Ending Dec 2023 for IMBIE validation; 2024 evaluated separately. |

---

## 2. Reconstructed Basin-Level Trajectories (1979–2024)

![Basin Volume Trajectories](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_2_basin_volume_trajectories.png)

### Table 2: Decadal Reconstructed Grounded Ice-Equivalent Volume Trajectories ($\text{km}^3$)

| Year | Epoch | Hp-I ($\text{km}^3$) | I-Ipp ($\text{km}^3$) | Ipp-J ($\text{km}^3$) | Domain A Central ($\text{km}^3$) | Domain A Low ($\text{km}^3$) | Domain A High ($\text{km}^3$) | Bedmap3 Central ($\text{km}^3$) | BedMachine Central ($\text{km}^3$) | Structural $\Delta$ ($\text{km}^3$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1979** | Epoch 1 | -42.42 | -24.30 | -15.65 | **-82.38** | -82.38 | -82.38 | 133,415.21 | 140,620.13 | +7,204.92 |
| **1985** | Epoch 1 | -60.42 | -36.56 | -23.50 | **-120.48** | -118.23 | -132.88 | 133,377.11 | 140,582.03 | +7,204.92 |
| **1989** | Epoch 1 | -45.73 | -35.19 | -16.87 | **-97.79** | -88.79 | -124.78 | 133,399.80 | 140,604.72 | +7,204.92 |
| **1995** | Epoch 1 | -107.66 | -81.08 | -43.39 | **-232.13** | -183.00 | -294.89 | 133,265.46 | 140,470.38 | +7,204.92 |
| **1999** | Epoch 1 | -88.55 | -80.17 | -54.32 | **-223.04** | -113.72 | -339.45 | 133,274.55 | 140,479.47 | +7,204.92 |
| **2002** | Epoch 2 | -103.19 | -97.61 | -76.12 | **-276.92** | -143.06 | -421.14 | 133,220.67 | 140,425.59 | +7,204.92 |
| **2006** | Epoch 2 | -93.58 | -105.63 | -150.53 | **-349.74** | -183.17 | -531.04 | 133,147.85 | 140,352.77 | +7,204.92 |
| **2010** | Epoch 2 | -144.15 | -150.55 | -232.18 | **-526.88** | -329.83 | -734.98 | 132,970.71 | 140,175.63 | +7,204.92 |
| **2013** | Epoch 2 | -175.60 | -183.39 | -314.68 | **-673.67** | -449.84 | -919.85 | 132,823.92 | 140,028.84 | +7,204.92 |
| **2018** | Epoch 3 | -193.30 | -219.03 | -395.73 | **-808.06** | -544.75 | -1,105.74 | 132,689.53 | 139,894.45 | +7,204.92 |
| **2023** | Epoch 3 | -195.01 | -241.06 | -471.62 | **-907.69** | -602.07 | -1,246.57 | 132,589.90 | 139,794.82 | +7,204.92 |
| **2024** | Epoch 3 | -201.90 | -249.89 | -489.49 | **-941.28** | -627.48 | -1,289.42 | 132,556.31 | 139,761.23 | +7,204.92 |

*Full 46-year annual time series saved in [`reports/tables/annual_volume_trajectories.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_volume_trajectories.csv) and [`reports/tables/annual_mass_balance_components.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_mass_balance_components.csv).*

### Basin Dynamic Analysis:
1. **Basin `Ipp-J` (Eastern Graham Land):** Prior to 1995, volume loss was minimal ($-43.39\text{ km}^3$ by 1995). Following the January 1995 Larsen A collapse and March 2002 Larsen B collapse, dynamic discharge accelerated dramatically. Volume loss quadrupled from $-76.12\text{ km}^3$ (2002) to $-314.68\text{ km}^3$ (2013), and reached **$-489.49\text{ km}^3$** by 2024. Basin `Ipp-J` represents the epicenter of Peninsula dynamic drawdown.
2. **Basin `I-Ipp` (Western Graham Land):** Demonstrates sustained, linear volume loss ($-80.17\text{ km}^3$ by 1999; $-183.39\text{ km}^3$ by 2013; **$-249.89\text{ km}^3$** by 2024). Driven by continuous tidewater glacier terminus retreat in response to warming ocean waters and Southern Annular Mode atmospheric forcing.
3. **Basin `Hp-I` (Palmer Land West):** Experienced early acceleration following the 1989–1991 disintegration of the Wordie Ice Shelf (Fleming/Seller glaciers), reaching $-107.66\text{ km}^3$ by 1995. However, because the thick George VI Ice Shelf remained stable, loss rates moderated relative to its large area, reaching **$-201.90\text{ km}^3$** by 2024.

---

## 3. Scenario Divergence Across Epoch 1 & Dual Baseline Tracking

![Scenario Divergence](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_2_scenario_divergence.png)

### Strict Scenario Separation:
Because satellite velocities are unmeasured prior to 1996, the three 1979–1999 scenarios are maintained as distinct, non-averaged trajectories:
- **Low Scenario:** Assumes pre-collapse steady balance flux ($D = 165.0\text{ Gt/yr}$). Yields $-113.72\text{ km}^3$ by 1999 and $-627.48\text{ km}^3$ by 2024.
- **Central Scenario:** InSAR-calibrated IOM anchored to 1996 ERS snapshots with RACMO driving stress scaling. Yields $-223.04\text{ km}^3$ by 1999 and $-941.28\text{ km}^3$ by 2024.
- **High Scenario:** Glacier-specific historical unbuttressing (Wordie 1989–1991 surge, Larsen A 1995 3.2× surge, and tidewater calving feedback; **Larsen B collapse strictly prohibited**). Yields $-339.45\text{ km}^3$ by 1999 and $-1,289.42\text{ km}^3$ by 2024.
- **Scenario Spread Envelope:** The divergence between High and Low is **$225.73\text{ km}^3$ by 1999** and **$661.94\text{ km}^3$ by 2024**. This spread is reported as an explicit scenario envelope, **never disguised as statistical noise**.

### Dual Baseline Realizations:
On the common domain (Domain A: $216,062.2\text{ km}^2$), the two official baselines track the identical physical volume change $\Delta V(t)$:
- Bedmap3: $133,497.59\text{ km}^3 \rightarrow 132,556.31\text{ km}^3$ (2024).
- BedMachine: $140,702.51\text{ km}^3 \rightarrow 139,761.23\text{ km}^3$ (2024).
- The $+7,204.92\text{ km}^3$ structural discrepancy is preserved identically across every year.

---

## 4. Candidate Nunatak Sensitivity Evaluation (Hypotheses H1, H2, H3)

The 18,628 candidate nunatak cells ($4,608.52\text{ km}^2$, Bedmap3 ice-eq volume $620.32\text{ km}^3$) are tracked outside Domain A under three discrete hypotheses:

1. **Hypothesis H1 (Exposed Rock / BedMachine Truth):**
   - Ice volume is strictly $0.0\text{ km}^3$; $dH/dt = 0$.
   - Grounded ice volume across the Peninsula equals Domain A exactly ($132,556.31\text{ km}^3$ Bedmap3 / $139,761.23\text{ km}^3$ BedMachine in 2024).
2. **Hypothesis H2 (Stagnant Ice Mantle / Atmospheric-Only Response):**
   - Nunataks contain perched ice disconnected from marine dynamic gates ($D = 0$).
   - Mass change is driven strictly by local RACMO atmospheric accumulation. Cumulative SMB anomaly adds **$+1.58\text{ km}^3$** by 2024.
   - Nunatak volume evolves: $620.32\text{ km}^3 \rightarrow \mathbf{621.90\text{ km}^3}$ in 2024.
3. **Hypothesis H3 (Static Bookkeeping Offset):**
   - Maintained as an invariant scalar offset of **$620.32\text{ km}^3$** ($dH/dt = 0$).
   - Full Bedmap3 catalog total equals $132,556.31 + 620.32 = \mathbf{133,176.63\text{ km}^3}$ in 2024.
4. **Excluded Disagreements:** Floating shelves ($506.4\text{ km}^2$, $133.85\text{ km}^3$) and open fjords ($376.6\text{ km}^2$, $30.43\text{ km}^3$) remain permanently excluded from the grounded ice target.

---

## 5. Regional Benchmark Validation Against Otosaka et al. (2026) IMBIE

![IMBIE Validation](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_2_imbie_validation.png)

### Table 3: Summary of Regional Validation Against Official IMBIE Benchmark

| Metric | Source IMBIE-3 Value | Reconstructed Central Value | Residual (Rec - IMBIE) | Validation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Cumulative Mass Anomaly (Dec 2023)** | **$-816.97 \pm 108.77\text{ Gt}$** ($1\sigma$) | **$-832.35\text{ Gt}$** | **$-15.38\text{ Gt}$** | **CONSISTENT (within $0.14\sigma$)** |
| **Solid Ice Volume Equivalent (Dec 2023)**| $-890.92 \pm 118.61\text{ km}^3$ | **$-907.69\text{ km}^3$** | **$-16.77\text{ km}^3$** | **CONSISTENT ($1.9\%$ residual)** |
| **45-Year Record Consistency** | 45 overlapping years | 34 / 45 years within $1\sigma$ | Max residual: $+126.4\text{ Gt}$ (2010) | **100% within $2\sigma$ envelope** |
| **Year 2024 (Post-IMBIE Period)** | N/A (IMBIE ends Dec 2023) | **$-863.15\text{ Gt}$ ($-941.28\text{ km}^3$)** | N/A | Separated from validation |

*Full annual validation records saved in [`reports/tables/imbie_regional_validation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/imbie_regional_validation.csv).*

### Critical Methodological Caveat:
While the aggregate reconstructed mass change tracks the official IMBIE reconciled consensus remarkably well (ending within $15.4\text{ Gt}$ over a 45-year integration), **agreement at the regional sector level does NOT prove that individual basin trajectories are correct**. The regional consensus acts as an integral boundary constraint; basin-level partitioning remains subject to local flux-gate velocity and fjord topography uncertainties.

---

## 6. Uncertainty Budget & Covariance Evolution

![Uncertainty Evolution](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/figures/chart_phase3_2_uncertainty_evolution.png)

### Table 4: Uncertainty Components Evolution Across Epochs

| Epoch | Years | Measurement Rate $\sigma$ ($\text{km}^3/\text{yr}$) | Model SMB Rate $\sigma$ ($\text{km}^3/\text{yr}$) | GIA Rate $\sigma$ ($\text{km}^3/\text{yr}$) | Total Annual Rate $\sigma$ ($\text{km}^3/\text{yr}$) | Cumulative Statistical $\sigma$ ($\text{km}^3$) | Scenario Spread High-Low ($\text{km}^3$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Epoch 1 Start** | 1979 | $\pm 19.63$ | $\pm 14.47$ | $\pm 4.36$ | $\pm 24.78$ | $\pm 24.78$ | $0.00$ |
| **Epoch 1 End** | 1999 | $\pm 19.63$ | $\pm 28.52$ | $\pm 4.36$ | $\pm 34.90$ | $\pm 127.35$ | **$225.73$** |
| **Epoch 2 Mid** | 2006 | $\pm 10.91$ | $\pm 26.54$ | $\pm 6.00$ | $\pm 29.33$ | $\pm 134.40$ | $347.87$ |
| **Epoch 2 End** | 2013 | $\pm 10.91$ | $\pm 22.75$ | $\pm 6.00$ | $\pm 25.95$ | $\pm 138.83$ | $470.01$ |
| **Epoch 3 Mid** | 2018 | $\pm 5.45$ | $\pm 22.65$ | $\pm 5.45$ | $\pm 23.93$ | $\pm 140.75$ | $560.99$ |
| **Epoch 3 End** | 2024 | $\pm 5.45$ | $\pm 28.38$ | $\pm 5.45$ | $\pm 29.41$ | $\mathbf{\pm 142.60}$ | $\mathbf{661.94}$ |

*Full annual uncertainty budget saved in [`reports/tables/annual_uncertainty_budget.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_uncertainty_budget.csv) and provenance classifications in [`reports/tables/basin_reconstruction_provenance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/basin_reconstruction_provenance.csv).*

### Key Uncertainty Insights:
1. **Rate Uncertainty Drops Post-2014:** Measurement rate uncertainty dropped by $72\%$ from Epoch 1 ($\pm 19.63\text{ km}^3/\text{yr}$) to Epoch 3 ($\pm 5.45\text{ km}^3/\text{yr}$) due to continuous Sentinel-1 SAR constellation velocity tracking.
2. **Dominance of Atmospheric Model Uncertainty:** RACMO SMB physics and coastal downscaling remain the largest single annual rate uncertainty source ($\pm 22\text{ to }28\text{ km}^3/\text{yr}$).
3. **Scenario Uncertainty Exceeds Statistical Sigma:** In Epoch 1, the unmeasured dynamic discharge spread ($225.73\text{ km}^3$) exceeds the statistical $1\sigma$ envelope ($\pm 127.35\text{ km}^3$). By 2024, the scenario spread reaches $661.94\text{ km}^3$, demonstrating why maintaining three explicit scenario branches is essential for scientific integrity.

---

## 7. Delivery & Scientific Review Submission

All deliverables required for Phase 3.2 are complete:
- **Reports:**
  - [`reports/phase3_2_historical_reconstruction.md`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/phase3_2_historical_reconstruction.md)
  - Interactive Artifact: [`phase3_2_historical_reconstruction.md`](file:///C:/Users/akash/.gemini/antigravity/brain/52ad6ae8-887d-48db-85e7-7d53f431979f/phase3_2_historical_reconstruction.md)
- **Data Tables (`reports/tables/`):**
  - [`domain_and_baseline_reconciliation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/domain_and_baseline_reconciliation.csv)
  - [`annual_volume_trajectories.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_volume_trajectories.csv)
  - [`annual_mass_balance_components.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_mass_balance_components.csv)
  - [`annual_uncertainty_budget.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/annual_uncertainty_budget.csv)
  - [`basin_reconstruction_provenance.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/basin_reconstruction_provenance.csv)
  - [`imbie_regional_validation.csv`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/tables/imbie_regional_validation.csv)
- **Diagnostic Figures (`reports/figures/`):**
  - [`chart_phase3_2_basin_volume_trajectories.png`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/chart_phase3_2_basin_volume_trajectories.png)
  - [`chart_phase3_2_scenario_divergence.png`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/chart_phase3_2_scenario_divergence.png)
  - [`chart_phase3_2_imbie_validation.png`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/chart_phase3_2_imbie_validation.png)
  - [`chart_phase3_2_uncertainty_evolution.png`](file:///c:/Users/akash/OneDrive/Desktop/mlbasics/antarctic-ice-volume-prediction/reports/figures/chart_phase3_2_uncertainty_evolution.png)

### Strict Stopping Condition Compliance:
No machine-learning models have been trained and no 2100 predictions have been generated. Execution stops here for scientific review and approval before proceeding to Phase 4 (Machine Learning Architecture & Predictive Modeling).

