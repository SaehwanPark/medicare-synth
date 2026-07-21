"""Unit tests for TabDatSynthAdapter, VerticalExpander, HorizontalExpander, and CLI expand command."""

from medicare_synth.cli import main as cli_main
from medicare_synth.expansion import (
    HorizontalExpander,
    TabDatSynthAdapter,
    VerticalExpander,
)
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import RelationalValidator


def test_tabdat_synth_adapter():
    """Test feature synthesis via TabDatSynthAdapter."""
    scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
    adapter = TabDatSynthAdapter()
    synth_df = adapter.synthesize_table(
        scenario_slice.bene_df, target_columns=["SYN_RISK_SCORE"]
    )

    assert "SYN_RISK_SCORE" in synth_df.columns
    assert synth_df.height == scenario_slice.bene_df.height


def test_vertical_expander():
    """Test vertical feature expansion across dataset tables."""
    scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
    tables = {
        "beneficiary_summary": scenario_slice.bene_df,
        "carrier_claims": scenario_slice.carrier_df,
        "outpatient_claims": scenario_slice.outpatient_df,
    }

    expander = VerticalExpander()
    expanded_tables = expander.expand_slice(tables)

    assert "SYN_RISK_SCORE" in expanded_tables["beneficiary_summary"].columns
    assert "SYN_CHRONIC_INDEX" in expanded_tables["beneficiary_summary"].columns
    assert expanded_tables["carrier_claims"].height == scenario_slice.carrier_df.height


def test_horizontal_expander_subgraph_scaling_and_relational_validation():
    """Test connected-subgraph scaling, key re-keying, and relational validator compatibility."""
    scenario_slice = ScenarioCompiler.get_scenario("valid_baseline_cohort")
    tables = {
        "beneficiary_summary": scenario_slice.bene_df,
        "carrier_claims": scenario_slice.carrier_df,
        "outpatient_claims": scenario_slice.outpatient_df,
    }

    expander = HorizontalExpander()
    scale_factor = 3
    scaled = expander.expand_subgraph(tables, scale_factor=scale_factor)

    assert (
        scaled["beneficiary_summary"].height
        == scenario_slice.bene_df.height * scale_factor
    )
    assert (
        scaled["carrier_claims"].height
        == scenario_slice.carrier_df.height * scale_factor
    )
    assert (
        scaled["outpatient_claims"].height
        == scenario_slice.outpatient_df.height * scale_factor
    )

    # Validate relational integrity of the horizontally scaled subgraph dataset
    validator = RelationalValidator()
    report = validator.validate_slice(
        bene_df=scaled["beneficiary_summary"],
        carrier_df=scaled["carrier_claims"],
        outpatient_df=scaled["outpatient_claims"],
    )

    assert report.is_valid is True


def test_cli_expand_subcommand(capsys):
    """Test CLI expand command for vertical and horizontal modes."""
    rc_vert = cli_main(
        ["expand", "--mode", "vertical", "--scenario", "valid_baseline_cohort"]
    )
    assert rc_vert == 0
    captured_vert = capsys.readouterr()
    assert "Vertical Expansion" in captured_vert.out

    rc_horiz = cli_main(
        [
            "expand",
            "--mode",
            "horizontal",
            "--scenario",
            "valid_baseline_cohort",
            "--scale",
            "2",
        ]
    )
    assert rc_horiz == 0
    captured_horiz = capsys.readouterr()
    assert "Horizontal Subgraph Expansion" in captured_horiz.out
