from contracts.base import TokenBase

from utils.file_manager import FileManager

from src.paths import (TempFiles,
                       TOKENS_ABI_DIR)

from loguru import logger


class Tokens:
    def __init__(self):
        self.all_tokens_data_from_file = FileManager().read_data_from_json_file(TempFiles().TOKENS_JSON_FILE)
        self.all_tokens = self._get_all_token_objs()

    def _get_all_token_objs(self):
        if not self.all_tokens_data_from_file:
            raise ValueError("No tokens found, please add valid tokens in contracts/tokens.json file")

        try:
            all_token_objs = []
            for token_data in self.all_tokens_data_from_file:
                token_obj = TokenBase(**token_data)
                token_abi = self._get_token_abi(symbol=token_obj.symbol)
                if token_abi is None:
                    continue

                token_obj.abi = token_abi
                all_token_objs.append(token_obj)

            return all_token_objs
        except Exception as e:
            logger.error(f"Error while creating token objects: {e}")
            exit(1)

    def _get_token_abi(self,
                       symbol: str):
        return FileManager.read_abi_from_file(f"{TOKENS_ABI_DIR}\\{symbol.lower()}.abi")

    def update_tokens_data(self):
        self.all_tokens_data_from_file = FileManager().read_data_from_json_file(TempFiles().TOKENS_JSON_FILE)
        self.all_tokens = self._get_all_token_objs()

    def get_by_name(self, name_query):
        for token in self.all_tokens:
            if token.symbol.lower() == name_query.lower():
                return token
        logger.error(f"Token {name_query} not found")
        return None

    def get_cg_id_by_name(self, name_query):
        for token in self.all_tokens:
            if token.symbol.lower() == name_query.lower():
                return token.coin_gecko_id
        logger.error(f"Token {name_query} not found")
        return None

    def get_tokens_by_protocol(
            self,
            protocol: str
    ) -> list:
        tokens = []
        for token in self.all_tokens:
            if protocol.lower() in token.available_protocol:
                tokens.append(token)
        return tokens
