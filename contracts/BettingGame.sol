pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract BettingGame is VRFConsumerBase {

    uint256 public fee;
    bytes32 public keyhash;
    address payable admin;

    uint256 public gameCount = 0;
    mapping(uint256 => Game) public games;
    mapping(bytes32 => uint256) public requestIdToGameIdMapping;

    struct Game {
        uint256 id;
        bool head;
        uint256 amount;
        address payable player;
    }

    event RequestedRandomness(bytes32 requestId);
    event Withdraw(address admin, uint256 amount);
    event Received(address indexed sender, uint256 amount);
    event Result(uint256 indexed gameId, address player, uint256 amount, bool won);

    constructor(
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        admin = payable(msg.sender);
        fee = _fee;
        keyhash = _keyhash;
    }

    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, 'caller is not the admin');
        _;
    }

    // _head represents whether player has chosen Head or not
    function play(bool _head) public payable returns (uint256){
        require(msg.value >= 10 ** 15, "BettingGame: minimum allowed bet is 0.001 ether");
        require(address(this).balance >= 2 * msg.value, "BettingGame: insufficient vault balance");
        require(LINK.balanceOf(address(this)) >= fee, "BettingGame: insufficient LINK token");

        gameCount++;
        games[gameCount] = Game(gameCount, _head, msg.value, payable(msg.sender));

        bytes32 requestId = requestRandomness(keyhash, fee);
        requestIdToGameIdMapping[requestId] = gameCount;

        emit RequestedRandomness(requestId);

        return gameCount;
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        // even number represents Head, odd number represents Tail
        bool head = _randomness % 2 == 0;

        uint256 gameId = requestIdToGameIdMapping[_requestId];
        Game memory game = games[gameId];
        bool playerWon = head == game.head;

        if (playerWon) {
            uint256 winAmount = 2 * game.amount;
            game.player.transfer(winAmount);
        }

        emit Result(gameId, game.player, game.amount, playerWon);
    }

    function withdrawLink(uint256 amount) external onlyAdmin {
        require(LINK.transfer(msg.sender, amount), "BettingGame: LINK transfer failed");
    }

    function withdrawEther(uint256 amount) external payable onlyAdmin {
        require(address(this).balance >= amount, "BettingGame: insufficient balance");
        admin.transfer(amount);

        emit Withdraw(admin, amount);
    }
}
