// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GasOptimization {
    struct Data {
        uint256 id;
        bytes content;
    }

    mapping(uint256 => Data) private dataStorage;

    event DataStored(uint256 id, bytes content);

    // Function to store data
    function storeData(uint256 id, bytes memory content) public {
        dataStorage[id] = Data(id, content);
        emit DataStored(id, content);
    }

    // Function to retrieve data
    function getData(uint256 id) public view returns (bytes memory) {
        return dataStorage[id].content;
    }
}
