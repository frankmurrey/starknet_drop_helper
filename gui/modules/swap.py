from typing import Callable
from typing import Union
from tkinter import messagebox


from gui.modules.txn_settings_frame import TxnSettingFrame
from contracts.tokens.main import Tokens
from src import enums

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable
from loguru import logger

from gui.modules.txn_settings_frame import TxnSettingFrame
from contracts.tokens.main import Tokens
from src import enums
from src.schemas import tasks


class SwapTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        swap_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.swap_frame = SwapFrame(
            master=self.tabview.tab(tab_name),
            grid=swap_frame_grid
        )

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_grid
        )

    def get_config_schema(self) -> Union[Callable, None]:
        swap_protocol = self.swap_frame.protocol_combo.get().lower()
        if swap_protocol == enums.ModuleName.JEDI_SWAP:
            return tasks.JediSwapTask

        elif swap_protocol == enums.ModuleName.SITHSWAP:
            return tasks.SithSwapTask

        elif swap_protocol == enums.ModuleName.MY_SWAP:
            return tasks.MySwapTask

        elif swap_protocol == enums.ModuleName.AVNU:
            return tasks.AvnuSwapTask

        elif swap_protocol == enums.ModuleName.K10SWAP:
            return tasks.K10SwapTask

        else:
            return None

    def build_config_data(self):
        # TODO: add validation for all fields
        # TODO: add
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: tasks.SwapTaskBase = config_schema(
                coin_to_swap=self.swap_frame.coin_to_swap_combo.get(),
                coin_to_receive=self.swap_frame.coin_to_receive_combo.get(),
                min_amount_out=self.swap_frame.min_amount_entry.get(),
                max_amount_out=self.swap_frame.max_amount_entry.get(),
                use_all_balance=self.swap_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.swap_frame.send_percent_balance_checkbox.get(),
                slippage=self.swap_frame.slippage_entry.get(),
                max_price_difference_percent=self.swap_frame.max_price_difference_percent_entry.get(),
                compare_with_cg_price=self.swap_frame.compare_with_cg_price_checkbox.get(),
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error",
                message=error_messages
            )
            return None


class SwapFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

        self.protocol_label = customtkinter.CTkLabel(
            self.frame,
            text="Protocol:"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.protocol_combo = customtkinter.CTkComboBox(
            self.frame,
            values=self.protocol_options,
            width=120,
            command=self.protocol_change_event
        )
        self.protocol_combo.grid(
            row=1,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.coin_to_swap_label = customtkinter.CTkLabel(
            self.frame,
            text="Coin to swap:"
        )
        self.coin_to_swap_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.coin_to_swap_combo = customtkinter.CTkComboBox(
            self.frame,
            values=self.coin_to_swap_options,
            width=120,
            command=self.update_coin_options
        )
        self.coin_to_swap_combo.grid(
            row=3,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.coin_to_receive_label = customtkinter.CTkLabel(
            self.frame,
            text="Coin to receive:"
        )
        self.coin_to_receive_label.grid(
            row=2,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.coin_to_receive_combo = customtkinter.CTkComboBox(
            self.frame,
            width=120,
            values=self.coin_to_receive_options
        )
        self.coin_to_receive_combo.grid(
            row=3,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.min_amount_label = customtkinter.CTkLabel(
            self.frame,
            text="Min amount:"
        )
        self.min_amount_label.grid(
            row=4,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.min_amount_entry = customtkinter.CTkEntry(
            self.frame,
            width=120
        )
        self.min_amount_entry.grid(
            row=5,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_amount_label = customtkinter.CTkLabel(
            self.frame,
            text="Max amount:"
        )
        self.max_amount_label.grid(
            row=4,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.max_amount_entry = customtkinter.CTkEntry(
            self.frame,
            width=120
        )
        self.max_amount_entry.grid(
            row=5,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event
        )
        self.use_all_balance_checkbox.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18
        )
        self.send_percent_balance_checkbox.grid(
            row=7,
            column=0,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.slippage_label = customtkinter.CTkLabel(
            self.frame,
            text="Slippage (%):"
        )
        self.slippage_label.grid(
            row=8,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.slippage_entry = customtkinter.CTkEntry(
            self.frame,
            width=70,
            textvariable=Variable(value=2)
        )
        self.slippage_entry.grid(
            row=9,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_price_difference_percent_label = customtkinter.CTkLabel(
            self.frame,
            text="Max price difference (%):"
        )
        self.max_price_difference_percent_label.grid(
            row=8,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.max_price_difference_percent_entry = customtkinter.CTkEntry(
            self.frame,
            width=120,
            textvariable=Variable(value=2)
        )
        self.max_price_difference_percent_entry.grid(
            row=9,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.compare_with_cg_price_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Compare to Gecko price",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.compare_with_cg_price_checkbox_event
        )
        self.compare_with_cg_price_checkbox.grid(
            row=10,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )
        self.compare_with_cg_price_checkbox.select()

    @property
    def protocol_options(self) -> list:
        return [
            enums.ModuleName.SITHSWAP.upper(),
            enums.ModuleName.MY_SWAP.upper(),
            enums.ModuleName.AVNU.upper(),
            enums.ModuleName.K10SWAP.upper(),
            enums.ModuleName.JEDI_SWAP.upper()
        ]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get()

        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    @property
    def coin_to_swap_options(self) -> list:
        return self.protocol_coin_options

    @property
    def coin_to_receive_options(self) -> list:
        protocol_coin_options = self.protocol_coin_options
        coin_to_swap = self.coin_to_swap_combo.get().lower()

        return [
            coin.upper()
            for coin in protocol_coin_options
            if coin.lower() != coin_to_swap.lower()
        ]

    def update_coin_options(self, event=None):
        coin_to_swap_options = self.coin_to_swap_options
        self.coin_to_swap_combo.configure(values=coin_to_swap_options)

        coin_to_receive_options = self.coin_to_receive_options
        self.coin_to_receive_combo.configure(values=coin_to_receive_options)
        self.coin_to_receive_combo.set(coin_to_receive_options[1])

    def protocol_change_event(self, protocol=None):
        coin_to_swap_options = self.coin_to_swap_options
        self.coin_to_swap_combo.configure(values=coin_to_swap_options)
        self.coin_to_swap_combo.set(coin_to_swap_options[1])

        coin_to_receive_options = self.coin_to_receive_options
        self.coin_to_receive_combo.configure(values=coin_to_receive_options)
        self.coin_to_receive_combo.set(coin_to_receive_options[1])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )
        else:
            self.min_amount_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(
                state="normal"
            )

    def compare_with_cg_price_checkbox_event(self):
        if self.compare_with_cg_price_checkbox.get():
            self.max_price_difference_percent_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value=2)
            )
        else:
            self.max_price_difference_percent_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )

