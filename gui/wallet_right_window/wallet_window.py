import tkinter
import tkinter.messagebox
from typing import Callable, Union

import customtkinter
from pydantic import ValidationError

from gui import objects
from gui import constants
from src import enums
from src.schemas.wallet_data import WalletData
from src.schemas.proxy_data import ProxyData
from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
import config


class EmptyUiWalletData:
    name = None
    private_key = ""
    pair_address = ""
    proxy = None
    type = enums.PrivateKeyType.argent
    cairo_version = 1
    address = ""


class WalletFrame(customtkinter.CTkFrame):

    def __init__(
            self,
            master,
            on_wallet_save: Callable[[Union[WalletData, None]], None],
            wallet_data: WalletData = None,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.wallet_data = wallet_data
        if self.wallet_data is None:
            self.wallet_data = EmptyUiWalletData()

        self.on_wallet_save = on_wallet_save

        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(6, weight=1)

        # NAME
        self.name_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Name",
            textvariable=tkinter.StringVar(value=self.wallet_data.name),
            width=200,
        )
        self.name_entry.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY
        self.private_key_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Private key*",
            textvariable=tkinter.StringVar(value=self.wallet_data.private_key),
            width=200,
        )
        self.private_key_entry.grid(row=1, column=0, padx=10, pady=0, sticky="w")
        self.private_key_entry.bind("<FocusOut>", self.private_key_changed)

        self.invalid_entry_label = customtkinter.CTkLabel(
            self.private_key_entry,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.invalid_entry_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        # ADDRESS
        self.address_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Address",
            textvariable=tkinter.StringVar(value=self.wallet_data.address),
            width=200,
            state="disabled",
        )
        self.address_entry.entry.configure(fg_color="gray25", border_color="gray25")
        self.address_entry.grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # PAIR ADDRESS
        self.pair_address_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Pair address",
            textvariable=tkinter.StringVar(value=self.wallet_data.pair_address),
            width=200,
        )
        self.pair_address_entry.grid(row=3, column=0, padx=10, pady=0, sticky="w")
        self.pair_address_entry.bind("<FocusOut>", self.pair_address_changed)

        self.pair_address_type_label = customtkinter.CTkLabel(
            self.pair_address_entry,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.pair_address_type_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        # PROXY
        self.proxy_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Proxy",
            textvariable=tkinter.StringVar(
                value=self.wallet_data.proxy.to_string() if isinstance(self.wallet_data.proxy, ProxyData) else ""
            ),
            width=200,
        )
        self.proxy_entry.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY TYPE
        self.private_key_type_radio_var = tkinter.StringVar(
            value=self.wallet_data.type.value
        )

        self.argent_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            command=self.toggle_wallet_type,
        )
        self.argent_radio_button.grid(row=5, column=0, padx=10, pady=(20, 10), sticky="w")

        self.braavos_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            command=self.toggle_wallet_type,
        )
        self.braavos_radio_button.grid(row=5, column=0, padx=110, pady=(20, 10), sticky="w")

        # CAIRO VERSION
        self.cairo_version_radio_var = tkinter.IntVar(value=self.wallet_data.cairo_version)

        self.cairo_version_radio_button_0 = customtkinter.CTkRadioButton(
            self,
            text="Cairo 0",
            variable=self.cairo_version_radio_var,
            value=0,
            command=self.toggle_cairo_version,
        )
        self.cairo_version_radio_button_0.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.cairo_version_radio_button_1 = customtkinter.CTkRadioButton(
            self,
            text="Cairo 1",
            variable=self.cairo_version_radio_var,
            value=1,
            command=self.toggle_cairo_version,
        )
        self.cairo_version_radio_button_1.grid(row=6, column=0, padx=110, pady=10, sticky="w")

        # ADD BUTTON
        self.add_button = customtkinter.CTkButton(
            self,
            text="Save",
            command=self.save_wallet_button_clicked,
        )
        self.add_button.grid(row=7, column=0, padx=10, pady=10, sticky="ws")

        self.__last_private_key_repr = ""
        self.__private_key = ""

    @property
    def private_key_type(self):
        return enums.PrivateKeyType[self.private_key_type_radio_var.get().strip()]

    @property
    def cairo_version(self):
        return self.cairo_version_radio_var.get()

    def set_private_key_invalid_label(self):
        self.invalid_entry_label.configure(text="Invalid key")

    def set_private_key_valid_label(self):
        self.invalid_entry_label.configure(text="")

    def set_address(self, private_key: str):
        if self.private_key_type == enums.PrivateKeyType.braavos:
            address = hex(get_braavos_addr_from_private_key(private_key, cairo_version=self.cairo_version))
        elif self.private_key_type == enums.PrivateKeyType.argent:
            address = hex(get_argent_addr_from_private_key(private_key, cairo_version=self.cairo_version))
        else:
            self.set_private_key_invalid_label()
            return

        address_repr = f"{address[:6]}.....{address[-6:]}"
        self.address_entry.entry.configure(
            textvariable=tkinter.StringVar(value=address_repr)
        )

    def toggle_wallet_type(self):
        try:
            self.set_address(self.__private_key)
            self.set_private_key_valid_label()

        except ValueError as e:
            self.set_private_key_invalid_label()
            return

    def toggle_cairo_version(self):
        if not self.__private_key:
            return

        try:
            self.set_address(self.__private_key)
            self.set_private_key_valid_label()

        except ValueError as e:
            self.set_private_key_invalid_label()
            return

    def private_key_changed(self, event):
        try:
            private_key = self.private_key_entry.get().strip()
            if not private_key:
                return

            if "....." in private_key:
                return

            elif len(private_key) != config.STARK_KEY_LENGTH:
                self.set_private_key_invalid_label()
                self.__last_private_key_repr = private_key
                return

            if private_key[:6] != self.__private_key[:6]:
                self.__private_key = private_key

            self.set_address(private_key)
            self.set_private_key_valid_label()

            private_key_repr = f"{private_key[:6]}.....{private_key[-6:]}"
            self.private_key_entry.entry.configure(
                textvariable=tkinter.StringVar(value=private_key_repr)
            )
            self.__last_private_key_repr = private_key_repr

        except ValueError as e:
            self.set_private_key_invalid_label()
            return

    def pair_address_changed(self, event):
        pair_address = self.pair_address_entry.get().strip()
        pair_address_length = len(pair_address)

        if pair_address_length == config.STARK_KEY_LENGTH:
            self.pair_address_type_label.configure(
                text="STARK", text_color=constants.SUCCESS_HEX
            )
        elif pair_address_length == config.EVM_ADDRESS_LENGTH:
            self.pair_address_type_label.configure(
                text="EVM", text_color=constants.SUCCESS_HEX
            )
        elif pair_address_length == 0:
            pass
        else:
            self.pair_address_type_label.configure(
                text="Invalid", text_color=constants.ERROR_HEX
            )

    def get_wallet_data(self) -> WalletData:
        private_key = self.private_key_entry.get().strip()
        if "....." in private_key:
            private_key = self.__private_key

        name = self.name_entry.get().strip()
        pair_address = self.pair_address_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        private_key_type = self.private_key_type
        cairo_version = self.cairo_version

        wallet_data = WalletData(
            name=name,
            private_key=private_key,
            pair_address=pair_address,
            proxy=proxy,
            type=private_key_type,
            cairo_version=cairo_version,
        )

        return wallet_data

    def save_wallet_button_clicked(self):
        wallet_data = None

        try:
            wallet_data = self.get_wallet_data()
        except ValidationError as e:
            error_messages = e.errors()[0]["msg"]
            tkinter.messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            self.focus_force()

        self.on_wallet_save(wallet_data)


class WalletWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            wallet_data: WalletData = None,
            on_wallet_save: Callable[[WalletData], None] = None
    ):
        super().__init__(master)

        self.title("Add wallet")
        self.geometry("300x450")

        self.after(10, self.focus_force)

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = WalletFrame(
            self,
            on_wallet_save=on_wallet_save,
            wallet_data=wallet_data,
        )

    def close(self):
        self.frame.destroy()
        self.destroy()
