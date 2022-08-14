// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/mocks/VRFCoordinatorV2Mock.sol";

contract MockVRFCoordinatorV2 is VRFCoordinatorV2Mock {

    constructor() VRFCoordinatorV2Mock(100000, 100000) {

    }

}