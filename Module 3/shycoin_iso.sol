//SPDX-License-Identifier: GPL-3.0

pragma solidity >0.4.0;

contract shycoin_ico{

    // Introduicng the max no of shycoins available for sale
    uint public max_shycoins = 1000000;

    // Conversion rate for shycoin
    uint public inr_to_shycoins = 10;

    // Introducing the total number of shycoins bought by the investors
    uint public total_shycoins_bought = 0;

    // Mapping from the investor address to its equity in shycoins and USD
    mapping(address => uint) holding_shycoin;
    mapping(address => uint) holding_inr;

    modifier can_buy_shycoins(uint inr_invested) {
        require (inr_invested*inr_to_shycoins + total_shycoins_bought <= max_shycoins);
        _;
    }

    // Getting the equity in shycoins as an investor
    function equity_in_shycoins(address investor) external constant returns (uint){
        return holding_shycoin[investor];
    }

    // Getting the equity in INR of an investor
    function equity_in_inr(address investor) external constant returns (uint){
        return holding_inr[investor];
    }

    // Buying shycoins
    function buy_shycoins(address investor, uint inr_invested) external
    can_buy_shycoins(inr_invested){
        uint shycoins_bought = inr_invested/inr_to_shycoins;
        holding_shycoin[investor] += shycoins_bought;
        holding_inr[investor] += inr_invested;
        total_shycoins_bought += shycoins_bought;
    } 

    // Buyback option for shycoins
    function sell_shycoins(address investor, uint shycoins_available) external{
        uint inr_got = shycoins_available*inr_to_shycoins;
        holding_shycoin[investor] -= shycoins_available;
        holding_inr[investor] -= inr_got;
        total_shycoins_bought -= shycoins_available;
    } 

}