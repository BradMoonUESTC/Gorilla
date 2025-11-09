// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

/**
 * @title SimpleERC20
 * @dev Simple ERC20 token contract for testing
 */
contract SimpleERC20 {
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _totalSupply * 10**_decimals;
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    function transfer(address to, uint256 value) public returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        require(to != address(0), "Transfer to zero address");
        
        // Vulnerability 3: Insufficient integer overflow protection; may overflow in extreme cases
        unchecked {
            balanceOf[msg.sender] -= value;
            balanceOf[to] += value;
        }
        
        emit Transfer(msg.sender, to, value);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        require(to != address(0), "Transfer to zero address");
        
        balanceOf[from] -= value;
        balanceOf[to] += value;
        // Vulnerability 1: Does not decrease allowance, enabling repeated use of the approved amount
        // allowance[from][msg.sender] -= value;
        
        emit Transfer(from, to, value);
        return true;
    }
    
    function approve(address spender, uint256 value) public returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }
    
    function mint(address to, uint256 amount) public {
        require(to != address(0), "Mint to zero address");
        
        // Vulnerability 2: Anyone can mint tokens; no access control
        totalSupply += amount;
        balanceOf[to] += amount;
        
        emit Transfer(address(0), to, amount);
    }
    
    function burn(uint256 amount) public {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance to burn");
        
        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        
        emit Transfer(msg.sender, address(0), amount);
    }
    
    // Vulnerability 4: withdraw function is vulnerable to reentrancy
    function withdraw() public {
        uint256 amount = balanceOf[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // Dangerous: External call before state update
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
        
        // State is updated after the external call, exposing reentrancy risk
        balanceOf[msg.sender] = 0;
        totalSupply -= amount;
    }
    
    // Receive ETH
    receive() external payable {
        // Simple ETH deposit: 1:1 minting of tokens
        balanceOf[msg.sender] += msg.value;
        totalSupply += msg.value;
        emit Transfer(address(0), msg.sender, msg.value);
    }
}
