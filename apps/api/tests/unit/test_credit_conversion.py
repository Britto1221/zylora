from decimal import Decimal

from app.modules.credits.service import micro_usd_to_usd, usd_to_micro_usd


def test_credit_conversion_round_trip() -> None:
    value = Decimal("19.123456")
    assert micro_usd_to_usd(usd_to_micro_usd(value)) == value
