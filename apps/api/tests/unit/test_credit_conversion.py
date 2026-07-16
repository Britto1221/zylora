from decimal import Decimal

from app.modules.credits.service import micro_usd_to_usd, usd_to_micro_usd


def test_credit_conversion_round_trip() -> None:
    amount = Decimal("19.1234")
    assert micro_usd_to_usd(usd_to_micro_usd(amount)) == amount
