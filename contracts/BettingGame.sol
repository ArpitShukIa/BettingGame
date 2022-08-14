pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract BettingGame is VRFConsumerBaseV2 {

    address payable admin;

    VRFCoordinatorV2Interface COORDINATOR;
    bytes32 keyhash;
    uint64 subscriptionId;
    uint16 requestConfirmations = 3;
    uint32 numWords = 50;
    uint32 callbackGasLimit = 10 ** 7;

    uint256[] randomWords;

    uint256 public gameCount = 0;
    mapping(uint256 => Game) public games;

    struct Game {
        uint256 id;
        bool head;
        uint256 amount;
        address payable player;
    }

    event RequestedRandomness(uint256 requestId);
    event Withdraw(address admin, uint256 amount);
    event Received(address indexed sender, uint256 amount);
    event Result(uint256 indexed gameId, address player, uint256 amount, bool won);

    constructor(
        address _vrfCoordinator,
        bytes32 _keyhash,
        uint64 _subscriptionId
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        admin = payable(msg.sender);
        keyhash = _keyhash;
        subscriptionId = _subscriptionId;
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
        require(randomWords.length > 0, "BettingGame: random words unavailable");

        gameCount++;
        games[gameCount] = Game(gameCount, _head, msg.value, payable(msg.sender));

        uint256 randomWord = randomWords[randomWords.length - 1];
        randomWords.pop();

        // Even randomWord represents HEADS, odd represents TAILS
        bool head = randomWord % 2 == 0;
        bool playerWon = head == _head;

        if (playerWon) {
            uint256 winAmount = 2 * msg.value;
            payable(msg.sender).transfer(winAmount);
        }

        emit Result(gameCount, msg.sender, msg.value, playerWon);

        return gameCount;
    }

    function requestRandomWords() public onlyAdmin {
        // Will revert if subscription is not set and funded.
        uint256 requestId = COORDINATOR.requestRandomWords(
            keyhash,
            subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );

        emit RequestedRandomness(requestId);
    }

    function fulfillRandomWords(
        uint256 requestId,
        uint256[] memory _randomWords
    ) internal override {
        for (uint i = 0; i < _randomWords.length; i++) {
            randomWords.push(_randomWords[i]);
        }
    }

    function withdrawEther(uint256 amount) external onlyAdmin {
        require(address(this).balance >= amount, "BettingGame: insufficient balance");
        admin.transfer(amount);

        emit Withdraw(admin, amount);
    }
}
