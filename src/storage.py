import os
from typing import List

from loguru import logger

from src import paths
from src.schemas.app_config import AppConfigSchema
from src.schemas.logs import WalletActionSchema
from utlis.file_manager import FileManager


class Storage:
    __instance = None

    class __Singleton:

        def __init__(self):
            self.__app_config: AppConfigSchema = self.__load_app_config()
            self.__wallets_data = []

        def set_wallets_data(self, value):
            self.__wallets_data = value

        def add_wallet_data(self, value):
            self.__wallets_data.append(value)

        def clear_wallets_data(self):
            self.__wallets_data.clear()

        @property
        def wallets_data(self):
            return self.__wallets_data

        @property
        def app_config(self) -> AppConfigSchema:
            return self.__app_config

        def __load_app_config(self) -> AppConfigSchema:
            try:
                config_file_data = FileManager.read_data_from_json_file(paths.APP_CONFIG_FILE)
                return AppConfigSchema(**config_file_data)
            except Exception as e:
                logger.error(f"Error while loading app config: {e}")
                logger.exception(e)

        def update_app_config(self, config: AppConfigSchema):
            self.__app_config = config

    def __new__(cls):
        if not Storage.__instance:
            Storage.__instance = Storage.__Singleton()
        return Storage.__instance


class ActionStorage:
    __instance = None

    def __new__(cls):
        if not ActionStorage.__instance:
            ActionStorage.__instance = ActionStorage.__Singleton()
        return ActionStorage.__instance

    class __Singleton:

        def __init__(self):
            self.all_actions = []
            self.current_action: WalletActionSchema = WalletActionSchema()
            self.current_logs_dir = None

        def add_action(self, action_data: WalletActionSchema):
            if Storage().app_config.preserve_logs is False:
                return

            self.all_actions.append(action_data)

        def get_all_actions(self):
            return self.all_actions

        def get_current_action(self) -> WalletActionSchema:
            return self.current_action

        def update_current_action(self, action_data: WalletActionSchema):
            if Storage().app_config.preserve_logs is False:
                return

            self.current_action = action_data

        def set_current_logs_dir(self, new_logs_dir):
            if not os.path.exists(new_logs_dir):
                return

            self.current_logs_dir = new_logs_dir

        def get_current_logs_dir(self):
            return self.current_logs_dir

        def reset_all_actions(self):
            self.all_actions = []

        def reset_current_logs_dir(self):
            self.current_logs_dir = None

        def create_and_set_new_logs_dir(self):
            if Storage().app_config.preserve_logs is False:
                return

            self.set_current_logs_dir(FileManager.create_new_logs_dir())

