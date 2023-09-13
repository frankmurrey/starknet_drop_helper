from pydantic import BaseModel
from pydantic import validator

from src.exceptions import AppValidationError
from utlis import validation


class MinMaxAmountOutValidationMixin(BaseModel):

    use_all_balance: bool

    min_amount_out: float
    max_amount_out: float

    @validator("min_amount_out", pre=True, check_fields=False)
    def validate_min_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        value = validation.get_converted_to_float(value, "Min Amount Out")
        value = validation.get_positive(value, "Min Amount Out", include_zero=False)

        return value

    @validator("max_amount_out", pre=True, check_fields=False)
    def validate_max_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        if "min_amount_out" not in values:
            raise AppValidationError("Min Amount Out is required")

        value = validation.get_converted_to_float(value, "Max Amount Out")
        value = validation.get_positive(value, "Max Amount Out", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out"], "Max Amount Out")

        return value
