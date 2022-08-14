import os
import shutil

from brownie import network, config, BettingGame

from scripts.helpful_scripts import get_account, get_vrf_coordinator_contract, LOCAL_BLOCKCHAIN_ENVIRONMENTS


def deploy(update_frontend=False):
    account = get_account()
    vrf_coordinator, subscription_id = get_vrf_coordinator_contract()
    betting_game = BettingGame.deploy(
        vrf_coordinator.address,
        config["networks"][network.show_active()]["keyhash"],
        subscription_id,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
    )
    if update_frontend:
        update_front_end()
    return betting_game


def update_front_end():
    # Send the build folder
    src = "./build"
    dest = "./frontend/src/chain-info"
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print("Front end updated!")


def main():
    deploy(update_frontend=True)
