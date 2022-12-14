from brownie import MortgageBackedSecurities, DappToken, network, config
from scripts.helpful_scripts import get_account, get_contract
import shutil
import os
import yaml
import json
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")
investor_num = 100
borrower_num = 100
Total_investment = 10000
Tranche_1_investment = Total_investment * 0.6
Tranche_2_investment = Total_investment * 0.2
Tranche_3_investment = Total_investment * 0.2
no_borrowers_1 = Tranche_1_investment / 100
no_borrowers_2 = Tranche_2_investment / 100
no_borrowers_3 = Tranche_3_investment / 100
borrowers_1 = [100] * int(no_borrowers_1)
borrowers_2 = [100] * int(no_borrowers_2)
borrowers_3 = [100] * int(no_borrowers_3)
payment_1 = 0
payment_2 = 0
payment_3 = 0


def deploy_mbs(update_front_end_flag=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    mbs = MortgageBackedSecurities.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = dapp_token.transfer(
        MortgageBackedSecurities.address,
        dapp_token.totalSupply() - KEPT_BALANCE,
        {"from": account},
    )
    tx.wait(1)
    fau_token = get_contract("fau_token")
    weth_token = get_contract("weth_token")

    add_allowed_tokens(
        MortgageBackedSecurities,
        {
            dapp_token: get_contract("dai_usd_price_feed"),
            fau_token: get_contract("dai_usd_price_feed"),
            weth_token: get_contract("eth_usd_price_feed"),
        },
        account,
    )
    if update_front_end_flag:
        update_front_end()
    return MortgageBackedSecurities, dapp_token


def add_allowed_tokens(MortgageBackedSecurities, dict_of_allowed_token, account):
    for token in dict_of_allowed_token:
        MortgageBackedSecurities.addAllowedTokens(token.address, {"from": account})
        tx = MortgageBackedSecurities.setPriceFeedContract(
            token.address, dict_of_allowed_token[token], {"from": account}
        )
        tx.wait(1)
    return MortgageBackedSecurities


def update_front_end():
    print("Updating front end...")
    # The Build
    copy_folders_to_front_end("./build/contracts", "./front_end/src/chain-info")

    # The Contracts
    copy_folders_to_front_end("./contracts", "./front_end/src/contracts")

    # The ERC20
    copy_files_to_front_end(
        "./build/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.3.2/ERC20.json",
        "./front_end/src/chain-info/ERC20.json",
    )
    # The Map
    copy_files_to_front_end(
        "./build/deployments/map.json",
        "./front_end/src/chain-info/map.json",
    )

    # The Config, converted from YAML to JSON
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open(
            "./front_end/src/brownie-config-json.json", "w"
        ) as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def copy_files_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copyfile(src, dest)


def main():
    deploy_mbs(update_front_end_flag=True)
