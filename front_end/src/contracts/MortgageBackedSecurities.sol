// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MortgageBackedSecurities is ChainlinkClient, Ownable {
    string public name = "Mortgage Backed Securities";

    address[] public stakers;
    // token > address
    //mapping token balances of each account
    mapping(address => mapping(address => uint256)) public stakingBalance;
    //Gettinh number of unique tokens staked
    mapping(address => uint256) public uniqueTokensStaked;
    //mapping tokenPricefeed
    mapping(address => address) public tokenPriceFeedMapping;
    address[] public allowedTokens;

    //Function to add allowed tokens
    function addAllowedTokens(address token) public onlyOwner {
        allowedTokens.push(token);
    }

    //finction to set Price feed contract
    function setPriceFeedContract(address token, address priceFeed)
        public
        onlyOwner
    {
        tokenPriceFeedMapping[token] = priceFeed;
    }

    //function to stake tokens into the contract
    function stakeTokens(uint256 _amount, address token) public {
        // Require amount greater than 0
        require(_amount > 0, "amount cannot be 0");
        //Require the token is allowed
        require(tokenIsAllowed(token), "Token currently isn't allowed");
        //Updating the tokens stacked list
        updateUniqueTokensStaked(msg.sender, token);
        //Transfering the tokens into contract
        IERC20(token).transferFrom(msg.sender, address(this), _amount);
        //Updating Balance of the investor
        stakingBalance[token][msg.sender] =
            stakingBalance[token][msg.sender] +
            _amount;
        //Updating unique tokens list
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    //Function for borrowers to repay the tokens
    function repayTokens(uint256 _amount, address token) public {
        // Require amount greater than 0
        require(_amount > 0, "amount cannot be 0");
        //Require the token is allowed
        require(tokenIsAllowed(token), "Token currently isn't allowed");
        //Updating the tokens stacked list
        updateUniqueTokensStaked(msg.sender, token);
        //Transfering the tokens into contract
        IERC20(token).transferFrom(msg.sender, address(this), _amount);
        //Updating Balance of the investor
        stakingBalance[token][msg.sender] =
            stakingBalance[token][msg.sender] +
            _amount;
        //Updating unique tokens list
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    // Unstaking Tokens (Withdraw)
    function unstakeTokens(uint256 _amount, address token) public {
        // Fetch  balance
        require(_amount > 0, "amount cannot be 0");
        //Fetch balance of the investor
        uint256 balance = stakingBalance[token][msg.sender];
        //Require the balance to be greater than zero
        require(balance > 0, "staking balance cannot be 0");
        //Transfer the tokens to investor
        IERC20(token).transferFrom(address(this), msg.sender, _amount);
        //Update Balance
        stakingBalance[token][msg.sender] =
            stakingBalance[token][msg.sender] -
            _amount;
        //Update unique tokens staked list
        if (stakingBalance[token][msg.sender] == 0) {
            uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
        }
    }

    //Function to take loans from the contract
    function loanTokens(address token) public {
        // Fetch balance
        uint256 balance = stakingBalance[token][msg.sender];
        //Require the balance to be greater than zero
        require(balance > 0, "staking balance cannot be 0");
        //Transfer the tokens to borrower
        IERC20(token).transfer(msg.sender, balance);
        //Update the balance of the borrower
        stakingBalance[token][msg.sender] = 0;
        //Update unique tokens staked list
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    //Function to the the total value of tokens user has
    function getUserTotalValue(address user) public view returns (uint256) {
        uint256 totalValue = 0;
        //Get number of unique tokens staked
        if (uniqueTokensStaked[user] > 0) {
            for (
                uint256 allowedTokensIndex = 0;
                allowedTokensIndex < allowedTokens.length;
                allowedTokensIndex++
            ) {
                //Get value of individual tokens staked
                totalValue =
                    totalValue +
                    getUserTokenStakingBalanceEthValue(
                        user,
                        allowedTokens[allowedTokensIndex]
                    );
            }
        }
        return totalValue;
    }

    //Function to check the token is allowed
    function tokenIsAllowed(address token) public view returns (bool) {
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            if (allowedTokens[allowedTokensIndex] == token) {
                return true;
            }
        }
        return false;
    }

    //Function to update unique token staked
    function updateUniqueTokensStaked(address user, address token) internal {
        if (stakingBalance[token][user] <= 0) {
            uniqueTokensStaked[user] = uniqueTokensStaked[user] + 1;
        }
    }

    //Function to get value of all tokens staked in eth
    function getUserTokenStakingBalanceEthValue(address user, address token)
        public
        view
        returns (uint256)
    {
        //Check tokens are staked
        if (uniqueTokensStaked[user] <= 0) {
            return 0;
        }
        //Get Eth price of token
        (uint256 price, uint8 decimals) = getTokenEthPrice(token);
        return (stakingBalance[token][user] * price) / (10**uint256(decimals));
    }

    //Function to get value of a token staked in eth
    function getTokenEthPrice(address token)
        public
        view
        returns (uint256, uint8)
    {
        //Get eth pricefeed
        address priceFeedAddress = tokenPriceFeedMapping[token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        return (uint256(price), priceFeed.decimals());
    }
}
