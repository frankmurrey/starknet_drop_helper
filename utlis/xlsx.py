from src.storage import ActionStorage
import pandas as pd
from loguru import logger


def write_balance_data_to_xlsx(path,
                               data: list[dict],
                               coin_option):

    datapd = {
        "Wallet Address": [],
        "Balance": [],
        "Coin": []
    }

    for wallet in data:
        for addr, balance in wallet.items():
            datapd["Wallet Address"].append(addr)
            datapd["Balance"].append(balance)
            datapd["Coin"].append(coin_option)

    df = pd.DataFrame(datapd)
    try:
        df.to_excel(path, index=False)

        logger.warning(f"Balance data saved to {path}")
    except Exception as e:
        logger.error(f"Error while saving balance data to {path}: {e}")


def write_wallet_action_to_xlsx():
    action_storage = ActionStorage()
    action = action_storage.get_current_action()

    if not action:
        return
    try:
        data = {
            "Wallet Address": [],
            "Proxy": [],
            "Date Time": [],
            "Action Type": [],
            "Is Success": [],
            "Transaction Hash": [],
            "Status": []
        }

        data["Wallet Address"].append(action.wallet_address)
        data["Proxy"].append(action.proxy)
        data["Date Time"].append(action.date_time)
        data["Action Type"].append(action.action_type)
        data["Is Success"].append(action.is_success)
        data["Transaction Hash"].append(action.transaction_hash)
        data["Status"].append(action.status)

        df = pd.DataFrame(data)
        df.to_excel(f"{action_storage.get_current_logs_dir()}\\!all_logs.xlsx", index=False)

    except Exception as e:
        logger.error(f"Error while logging all actions to xlsx: {e}")
        return


def write_generated_wallets_to_xlsx(
        path: str,
        data: list[dict]
):
    datapd = {
        "Mn": [],
        "Pk": [],
        "Addr": [],
        "PubK": []
    }

    for wallet in data:
        datapd["Mn"].append(wallet["mnemonic"])
        datapd["Pk"].append(wallet["private_key"])
        datapd["Addr"].append(wallet["address"])
        datapd["PubK"].append(wallet["public_key"])

    df = pd.DataFrame(datapd)
    try:
        df.to_excel(path, index=False)

        logger.warning(f"Generated wallets saved to {path}")

    except Exception as e:
        logger.error(f"Error while saving generated wallets to {path}: {e}")


