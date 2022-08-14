from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import BettingGame, config, network


def deploy():
    account = get_account()
    betting_game = BettingGame.deploy(
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
    )
    return betting_game


def main():
    deploy()
