<USER_REQUEST>
# Stage 5.1 — Historical Transient Validation and Numerical Coupling Improvement

## Objective

Improve the coupling between evolving ice thickness and the 2D Shallow Shelf Approximation (SSA) velocity solution, then evaluate the calibrated Antarctic Peninsula model over an extended historical period.

Stage 5.0 is conditionally accepted. This stage must preserve its accepted results and restrictions while addressing its known numerical limitations.

This is a historical simulation and validation-readiness milestone. It does NOT authorize 2100 projections.

---

## 1. Freeze the accepted baseline

Before execution:

- Verify Stage 5.0 artifact hashes.
- Preserve the Stage 4.7 regional basal-friction parameters.
- Preserve Stage 4.8 physical constants and WGS84 metrics.
- Preserve grounded/floating domain definitions.
- Preserve the existing extreme-slope quality masks.
- Preserve the Stage 5.0 mass-conservation implementation.

Frozen basal friction:

- Hp-I: 8.168 × 10^6 Pa·(m/s)^(-1/3)
- I-Ipp: 1.200 × 10^7 Pa·(m/s)^(-1/3)
- Ipp-J: 1.550 × 10^7 Pa·(m/s)^(-1/3)

Frozen rheology:

- Glen exponent n = 3
- Rate factor A = 3.5 × 10^(-25) Pa^(-3) s^(-1)
- Ice density = 917 kg/m³
- Ocean density = 1028 kg/m³
- Schoof parameter = 0.61

Do not recalibrate these parameters during Stage 5.1.

---

## 2. Improve transient momentum-thickness coupling

Stage 5.0 updated SSA velocity at annual boundaries while thickness evolved at subannual intervals.

Investigate and implement a more consistent coupling strategy.

Evaluate:

A. Annual momentum update (Stage 5.0 baseline).

B. Periodic subannual momentum updates.

C. Momentum update based on a documented physical or numerical trigger, such as a threshold in thickness change, grounding-line displacement or velocity change.

Compare these strategies under identical forcing and initial conditions.

For each strategy, report:

- Momentum solve frequency.
- Picard iterations.
- Residual convergence.
- Computational cost.
- Velocity differences.
- Thickness differences.
- Grounding-line displacement.
- Mass conservation residual.

Do not assume that more frequent solves are automatically better. Demonstrate whether the improved coupling materially changes the solution.

---

## 3. Time-step restrictions

Retain the Stage 5.0 accepted maximum:

Δt ≤ 0.10 years.

Use 0.05 and 0.10 years as the primary comparison cases.

The 0.25 and 0.50 year configurations remain rejected.

Do not use negative-thickness clipping as a substitute for stability.

If a negative thickness occurs:

- Stop or reject the affected step.
- Record the cell and numerical state.
- Identify the cause.
- Correct the underlying numerical issue.
- Re-run the affected experiment.

No phantom mass may be introduced by clamping.

---

## 4. Extreme-slope and cliff-cell treatment

Stage 5.0 identified local numerical stagnation near steep alpine headwalls.

Do not automatically impose the proposed 5,000 m/yr velocity cap.

Instead:

- Inspect the affected cells.
- Compare raw and smoothed slope.
- Inspect local thickness, driving stress and velocity.
- Evaluate numerical stabilization options already compatible with the approved SSA formulation.
- Quantify the effects of each stabilization method on regional velocity, mass flux and grounding-line movement.

If a velocity cap is tested, it must be a separate sensitivity experiment, never silently applied to the primary solution.

Do not remove these cells from the physical forward domain.

---

## 5. Historical forcing extension

Inventory all usable historical RACMO2.3p2 forcing years.

Determine the longest defensible continuous historical period supported by:

- Actual annual SMB data.
- Consistent spatial coverage.
- Compatible geometry and observation epochs.
- Valid temporal metadata.

Do not assume that a dataset's full date range is usable without checking.

Use distinct annual forcing fields. Verify subannual integration so that each year's SMB is applied exactly once over that year.

If historical geometry is static, label the simulation as evolving thickness on fixed bed geometry. Do not imply that bedrock or all boundary geometry is dynamically updated.

---

## 6. Historical benchmark and validation design

Use IMBIE-3 only as an external reconciled benchmark, not as independent satellite validation.

Identify additional observations suitable for evaluation.

For every comparison, document:

- Source and DOI.
- Temporal coverage.
- Spatial resolution.
- Geographic footprint.
- Uncertainty.
- Whether the data contributed to Stage 4.7 calibration.
- Whether the data are genuinely independent of calibration.

Do not describe a calibration dataset as independent validation.

Where truly independent observations are unavailable, state that limitation explicitly.

Evaluate:

- Basin-level mass-change trends.
- Domain A mass-change trend.
- Grounded volume evolution.
- Grounding-line movement.
- Regional differences.
- Uncertainty ranges.

---

## 7. Conservation and numerical verification

For every simulation, record:

- Grounded mass.
- Floating mass.
- SMB contribution.
- Grounding-line transfer.
- Grounded calving.
- Floating-shelf calving.
- Basal melt, only where defensible forcing exists.
- Final mass.
- Numerical residual.
- Negative-thickness violations.

Internal grounded/floating transfers must cancel in the combined system ledger.

Preserve the distinction between numerical conservation and physical accuracy.

---

## 8. Required deliverables

Generate:

1. stage5_1_coupling_strategy_comparison.csv
2. stage5_1_momentum_convergence.csv
3. stage5_1_timestep_comparison.csv
4. stage5_1_historical_forcing_inventory.csv
5. stage5_1_historical_simulation_results.csv
6. stage5_1_observation_provenance.csv
7. stage5_1_regional_validation_metrics.csv
8. stage5_1_mass_conservation.csv
9. stage5_1_extreme_slope_sensitivity.csv
10. stage5_1_failure_and_limitation_register.csv
11. stage5_1_transient_diagnostics.png
12. stage5_1_closure_report.md

Include reproducible configuration files and input hashes.

---

## 9. Acceptance criteria

Stage 5.1 may pass if:

- The accepted time-step restriction is respected.
- Momentum-thickness coupling is explicitly evaluated.
- No artificial mass is introduced.
- Grounding-line migration remains numerically stable.
- The historical forcing is correctly indexed and integrated.
- Observation provenance is transparent.
- Model limitations and failed experiments are preserved.
- Improvements over Stage 5.0 are demonstrated quantitatively.

If the new coupling does not materially improve the result, retain the simpler method and document why.

---

## 10. Strict prohibitions

Do not:

- Generate 2100 projections.
- Train ML residual emulators.
- Change frozen basal-friction parameters.
- Change frozen rheological parameters.
- Force SMB and discharge into equilibrium.
- Invent missing forcing.
- Claim independent validation without provenance evidence.
- Hide failed experiments.
- Automatically advance to another stage.

## Final instruction

Execute Stage 5.1 as a controlled numerical and historical validation improvement.

Do not rerun unrelated earlier stages.

Stop after generating the deliverables and closure report. Present the evidence and final verdict for review.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-11-15T05:01:36+05:30.

The user's current state is as follows:
Active Document: c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\scratch\compile_stage4_2_2_report.py (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
Other open documents:
- c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\scratch\inspect_imbie_csv.py (LANGUAGE_UNSPECIFIED)
- c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\scratch\run_stage4_5_3_integration.py (LANGUAGE_UNSPECIFIED)
- c:\Users\akash\OneDrive\Desktop\mlbasics\antarctic-ice-volume-prediction\scratch\run_stage4_5_2_1_audit.py (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>