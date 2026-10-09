"""Published study constants transcribed from archived QC; not simulated outputs."""
SCENARIOS = {
    "S0": [],
    "J105": ["C2025_J105_7.0_7.5"],
    "FT01": ["C2025_FT01_19.6_20.0"],
    "FT003": ["C2025_FT003_9.1_10.0"],
    "J46": ["C2025_J46_2.0_2.3"],
    "MAR20_OBSERVED": ["C2025_J105_7.0_7.5", "C2025_FT01_19.6_20.0", "C2025_FT003_9.1_10.0"],
    "MAR21_OBSERVED": ["C2025_J46_2.0_2.3"],
    "EVENT_FOOTPRINT_UNION": ["C2025_J105_7.0_7.5", "C2025_FT01_19.6_20.0", "C2025_FT003_9.1_10.0", "C2025_J46_2.0_2.3"],
}
RESTORATION_ROADS = ["J105", "FT01", "FT003"]
REFERENCE_TARGETS = {
    "baseline_reachable_population": 1900604.0877224302,
    "baseline_mean_min": 7.210855926674443,
    "baseline_30min_coverage_pct": 99.62533094465734,
    "MAR20_newly_unreachable_population": 4961.045478571206,
    "MAR20_newly_unreachable_origins": 544,
    "MAR20_population_delayed_ge_1min": 11143.042743215337,
    "MAR20_delta_30min_pp": -0.26031867589394153,
    "J105_newly_unreachable_population": 3219.757496956736,
    "FT01_newly_unreachable_population": 1278.999496564269,
    "FT003_newly_unreachable_population": 462.2884850502014,
    "J46_newly_unreachable_population": 0.0,
}
# Fixed historical values are comparison targets only, never output in place of a computed value.
