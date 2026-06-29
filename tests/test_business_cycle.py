from aqtc.config import AQTCConfig
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR


def test_business_cycle_end_to_end(tmp_path):
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    assert result.accepted_strategy is True
    assert result.rejected_bad_strategy is True
    assert result.approval_status == "approved"
    assert result.portfolio_positions > 0
    assert result.gross_exposure <= 4.0
    assert result.stripe_net_usd == 17.0
    assert result.event_count >= 7
    assert result.spend_status == "completed"
