import random

from typing import Union

from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from loguru import logger

import config
from modules.base import StarkBase
from src.schemas.configs.identity import IdentityMintConfigSchema
from contracts.starknet_id.main import StarkNetIdContracts


class IdentityMint(StarkBase):
    config: IdentityMintConfigSchema
    account: Account

    def __init__(self,
                 account,
                 config: IdentityMintConfigSchema):
        super().__init__(client=account.client)

        self.account = account
        self.config = config

        self.stark_id_contracts = StarkNetIdContracts()
        self.router_contract = self.get_contract(address=self.stark_id_contracts.router_address,
                                                 abi=self.stark_id_contracts.router_abi,
                                                 provider=account)

        self.token_id = None

    async def check_if_id_exists(self, token_id: int) -> bool:
        try:
            owner = await self.router_contract.functions['ownerOf'].call(token_id)
            if owner:
                return True

        except ClientError:
            return False

    def get_random_stark_id(self):
        return random.randint(config.MIN_STARK_ID, config.MAX_STARK_ID)

    async def get_available_id_for_mint(
            self,
            max_retries: int,
    ) -> Union[int, None]:

        if max_retries == 0:
            return None

        random_id = self.get_random_stark_id()
        is_id_exists = await self.check_if_id_exists(token_id=random_id)
        if is_id_exists is True:
            await self.get_available_id_for_mint(max_retries=max_retries - 1)

        return random_id

    async def build_txn_payload_calls(self):
        random_id = await self.get_available_id_for_mint(max_retries=10)
        if random_id is None:
            logger.error('No available token id found in 10 tries')
            return None

        self.token_id = random_id
        mint_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='mint',
                                    call_data=[random_id])
        calls = [mint_call]

        return calls

    async def send_mint_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = f"StarkNet Identity Mint (token id: {self.token_id})"

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status






