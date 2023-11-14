import time
from datetime import datetime
from typing import Union

from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from src.schemas import tasks
from src.schemas.wallet_data import WalletData
from src.schemas.logs import WalletActionSchema
from src.schemas.action_models import ModuleExecutionResult
from src.storage import Storage
from src.storage import ActionStorage
from src.action_logger import ActionLogger

from src.proxy_manager import ProxyManager

from utils.key_manager.key_manager import get_key_pair_from_pk
from utils.repr.module import print_module_config
from utils.gas_price import GasPrice

from src import enums
import config as cfg


class ModuleExecutor:
    """
    Module executor for modules
    """

    def __init__(
            self,
            task: tasks.TaskBase,
            wallet: WalletData
    ):
        self.task = task
        self.module_name = task.module_name
        self.module_type = task.module_type
        self.storage = Storage()
        self.action_storage = ActionStorage()

        self.app_config = self.storage.app_config

        self.wallet_data = wallet

    async def start(self) -> ModuleExecutionResult:
        print_module_config(task=self.task)
        time.sleep(cfg.DEFAULT_DELAY_SEC)

        if not self.app_config.rpc_url:
            logger.error("Please, set RPC URL in tools window or app_config.json file")
            return ModuleExecutionResult(
                execution_status=False,
                execution_info="Set RPC URL in tools window or app_config.json file",
            )

        execute_status: ModuleExecutionResult = await self.execute_module(
            wallet_data=self.wallet_data, base_url=self.app_config.rpc_url
        )

        return execute_status

    async def execute_module(
            self,
            wallet_data: WalletData,
            base_url: str
    ) -> Union[ModuleExecutionResult, None]:
        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data)

        action_log_data = WalletActionSchema(
            date_time=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            wallet_address=wallet_data.address,
        )

        self.action_storage.update_current_action(action_data=action_log_data)
        key_pair = get_key_pair_from_pk(wallet_data.private_key)

        custom_session = proxy_manager.get_session()

        current_ip = await proxy_manager.get_ip()
        # TODO - логирование добавить
        if current_ip is None and proxy_data:
            err_msg = f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params"
            action_log_data.set_error(err_msg)

            return ModuleExecutionResult(
                execution_status=False,
                execution_info=err_msg,
            )

        logger.info(f"Current ip: {current_ip}")

        client = FullNodeClient(node_url=base_url, session=custom_session)

        if self.task.test_mode is False:
            gas_price = GasPrice(
                block_number=enums.BlockStatus.PENDING.value,
                session=custom_session
            )
            status, gas_price = await gas_price.check_loop(
                target_price_wei=self.app_config.target_gas_price * 10 ** 9,
                time_out_sec=self.app_config.time_to_wait_target_gas_price_sec,
                is_timeout_needed=self.app_config.is_gas_price_wait_timeout_needed
            )

            if gas_price is None:
                err_msg = f"Error while getting gas price"
                action_log_data.set_error(err_msg)
                return

            if status is False:
                err_msg = (
                    f"Gas price is too high ({gas_price / 10 ** 9} Gwei) after "
                    f"{self.app_config.time_to_wait_target_gas_price_sec}. Aborting transaction."
                )
                action_log_data.set_error(err_msg)
                return ModuleExecutionResult(
                    execution_status=False,
                    execution_info=err_msg,
                )

            logger.info(
                f"Gas price is under target value ({self.app_config.target_gas_price}), "
                f"now = {gas_price / 10 ** 9} Gwei."
            )
        else:
            logger.warning(f"Test mode enabled, gas price check is skipped")

        account = Account(
            address=wallet_data.address,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )

        retries = self.task.retries if self.task.test_mode is False else 1

        execution_status: ModuleExecutionResult
        if self.module_name == enums.ModuleName.DEPLOY:
            module = self.task.module(
                private_key=wallet_data.private_key,
                account=account,
                task=self.task,
                key_type=wallet_data.type,
            )
            execution_status = await module.try_send_txn(retries=retries)

        elif self.module_type == enums.ModuleType.TRANSFER:
            module = self.task.module(
                account=account,
                task=self.task,
                wallet_data=wallet_data
            )

            execution_status = await module.try_send_txn(retries=retries)

        elif self.module_type == enums.ModuleType.BRIDGE:
            module = self.task.module(
                account=account,
                task=self.task,
                wallet_data=wallet_data
            )

            execution_status = await module.try_send_txn(retries=retries)

        else:
            module = self.task.module(account=account, task=self.task)
            execution_status = await module.try_send_txn(retries=retries)

        if self.task.test_mode is False:
            action_log_data.module_name = self.module_name.value
            action_log_data.module_type = self.module_type.value

            action_log_data.is_success = execution_status.execution_status
            action_log_data.status = execution_status.execution_info
            action_log_data.transaction_hash = execution_status.hash

            action_logger = ActionLogger()
            action_logger.add_action_to_log_storage(action_data=action_log_data)
            action_logger.log_action_from_storage()

        await custom_session.close()
        await proxy_manager.close_connector()

        return execution_status
