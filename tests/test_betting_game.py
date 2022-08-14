import pytest
from brownie import exceptions

from scripts.deploy import deploy
from scripts.helpful_scripts import (
    get_account,
    ether,
    fund_with_link,
    get_contract,
)


@pytest.fixture
def betting_game():
    account = get_account()
    betting_game = deploy()

    account.transfer(betting_game.address, ether(10))
    fund_with_link(betting_game.address)

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

    # Bet amount less than 0.001 ether
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.play(True, {'from': player, 'value': 1})

    # Bet amount more than vault balance
    with pytest.raises(exceptions.VirtualMachineError):
        betting_game.play(True, {'from': player, 'value': ether(11)})

    tx = betting_game.play(True, {'from': player, 'value': ether(1)})
    game_id = tx.return_value
    request_id = tx.events["RequestedRandomness"]["requestId"]

    assert game_id == 1
    assert betting_game.gameCount() == 1
    assert betting_game.games(1) == (1, True, ether(1), player)
    assert betting_game.requestIdToGameIdMapping(request_id) == game_id


def test_winning_bet(betting_game):
    account = get_account()
    player = get_account(index=1)
    bet_amount = ether(1)

    player_initial_balance = player.balance()
    contract_initial_balance = betting_game.balance()

    tx = betting_game.play(True, {'from': player, 'value': bet_amount})
    request_id = tx.events["RequestedRandomness"]["requestId"]

    requested_random_number = 10  # Even number represents a Head

    tx = get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, requested_random_number, betting_game.address, {"from": account}
    )

    assert player.balance() == player_initial_balance + bet_amount
    assert betting_game.balance() == contract_initial_balance - bet_amount

    assert tx.events['Result']['gameId'] == 1
    assert tx.events['Result']['player'] == player
    assert tx.events['Result']['amount'] == bet_amount
    assert tx.events['Result']['won']


def test_losing_bet(betting_game):
    account = get_account()
    player = get_account(index=1)
    bet_amount = ether(1)

    player_initial_balance = player.balance()
    contract_initial_balance = betting_game.balance()

    tx = betting_game.play(True, {'from': player, 'value': bet_amount})

    request_id = tx.events["RequestedRandomness"]["requestId"]

    requested_random_number = 11  # Odd number represents a Tail

    tx = get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, requested_random_number, betting_game.address, {"from": account}
    )

    assert player.balance() == player_initial_balance - bet_amount
    assert betting_game.balance() == contract_initial_balance + bet_amount

    assert tx.events['Result']['gameId'] == 1
    assert tx.events['Result']['player'] == player
    assert tx.events['Result']['amount'] == bet_amount
    assert not tx.events['Result']['won']
