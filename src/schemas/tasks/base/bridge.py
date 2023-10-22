from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase


class BridgeTaskBase(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_x: str
    dst_chain: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    min_amount_out: float
    max_amount_out: float

    @property
    def action_info(self):
        return self.coin_x.upper()