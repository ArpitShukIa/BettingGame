from brownie import accounts, network, config, MockVRFCoordinatorV2, Contract
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_vrf_coordinator_contract():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(MockVRFCoordinatorV2) <= 0:
            account = get_account()
            # deploy mock
            MockVRFCoordinatorV2.deploy({"from": account})
            MockVRFCoordinatorV2[-1].createSubscription()
        contract = MockVRFCoordinatorV2[-1]
        subscription_id = 1
    else:
        contract_address = config["networks"][network.show_active()]["vrf_coordinator"]
        contract = Contract.from_abi(
            MockVRFCoordinatorV2._name, contract_address, MockVRFCoordinatorV2.abi
        )
        subscription_id = config["networks"][network.show_active()]["vrf_coordinator_subscription_id"]

    return contract, subscription_id


def ether(amount):
    return Web3.toWei(amount, 'ether')
