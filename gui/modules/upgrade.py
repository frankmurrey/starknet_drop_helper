from src.schemas import tasks

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


class UpgradeTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.UpgradeTask = None
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 0,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            },
            task=task
        )

        text_box_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = (f"- Wallets will be upgraded from Cairo 0 → Cairo 1\n\n"
                f"- P.S Braavos wallets doesn't support upgrade yet") \

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
        )

    def build_config_data(self):
        return tasks.UpgradeTask(
            max_fee=self.txn_settings_frame.max_fee_entry.get(),
            forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
        )
