from aqtc.financial_core.harness import HarnessGenotype, build_harness


def test_harness_builds_from_default_genotype():
    genotype = HarnessGenotype()
    harness = build_harness(genotype)
    assert genotype.dim() == 19
    assert sorted(harness.features.keys()) == [
        "cross_sectional",
        "macd",
        "pca",
        "rsi",
        "wavelet",
        "zscore",
    ]
    assert type(harness.risk).__name__ == "CompositeRiskTool"
    assert type(harness.execution).__name__ == "CompositeExecutionTool"
