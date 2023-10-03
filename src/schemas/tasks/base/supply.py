from typing import Union

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase


class SupplyTaskBase(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_to_supply: str

    use_all_balance: bool = False
    send_percent_balance: bool = False
    enable_collateral: bool = False

    min_amount_out: float
    max_amount_out: float

    @property
    def action_info(self):
        return f"{self.coin_to_supply.upper()}"
