import pytest
from brownie import exceptions

from scripts.deploy import deploy
from scripts.helpful_scripts import get_account, ether, get_vrf_coordinator_contract


@pytest.fixture
def betting_game():
    account = get_account()
    betting_game = deploy()

    vrf_coordinator, _ = get_vrf_coordinator_contract()
    vrf_coordinator.addConsumer(1, betting_game.address)
    vrf_coordinator.fundSubscription(1, ether(10))

    tx = betting_game.requestRandomWords()
    request_id = tx.events['RequestedRandomness']['requestId']

    vrf_coordinator.fulfillRandomWordsWithOverride(request_id, betting_game.address, list(range(0, 50)))

    account.transfer(betting_game.address, ether(10))

    return betting_game


def test_received_event_emitted_on_payment(betting_game):
    account = get_account()
    tx = account.transfer(betting_game.address, 1)

    assert tx.events['Received']['sender'] == account
    assert tx.events['Received']['amount'] == 1


def test_ether_withdraw(betting_game):
    admin = get_account()
    non_admin = get_account(index=1)

    # Cannot withdraw more than balance
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.withdrawEther(ether(20), {'from': admin})

    # Non-admin cannot withdraw ether
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.withdrawEther(ether(10), {'from': non_admin})

    initial_admin_balance = admin.balance()
    tx = betting_game.withdrawEther(ether(10), {'from': admin})

    assert admin.balance() > initial_admin_balance
    assert tx.events['Withdraw']['admin'] == admin
    assert tx.events['Withdraw']['amount'] == ether(10)


def test_can_play_game(betting_game):
    player = get_account(index=1)
    bet_amount = ether(1)

    player_initial_balance = player.balance()
    contract_initial_balance = betting_game.balance()

    # Bet amount less than 0.001 ether
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.play(True, {'from': player, 'value': 1})

    # Bet amount more than vault balance
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.play(True, {'from': player, 'value': ether(11)})

    # Player will lose this game as randomNumber used here will be 49 and 49 % 2 == 1
    tx = betting_game.play(True, {'from': player, 'value': bet_amount})

    assert tx.return_value == 1
    assert tx.events['Result']['gameId'] == 1
    assert tx.events['Result']['player'] == player
    assert tx.events['Result']['amount'] == bet_amount
    assert not tx.events['Result']['won']

    assert betting_game.gameCount() == 1
    assert betting_game.games(1) == (1, True, bet_amount, player)

    assert player.balance() == player_initial_balance - bet_amount
    assert betting_game.balance() == contract_initial_balance + bet_amount

    # Player will win this game as randomNumber used here will be 48 and 48 % 2 == 0
    tx = betting_game.play(True, {'from': player, 'value': bet_amount})

    assert tx.return_value == 2
    assert tx.events['Result']['gameId'] == 2
    assert tx.events['Result']['player'] == player
    assert tx.events['Result']['amount'] == bet_amount
    assert tx.events['Result']['won']

    assert betting_game.gameCount() == 2
    assert betting_game.games(2) == (2, True, bet_amount, player)

    # Player will win the lost money here
    assert player.balance() == player_initial_balance
    assert betting_game.balance() == contract_initial_balance
