// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

/**
 * @title SimpleERC20
 * @dev 简单的ERC20代币合约，用于测试
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
        
        // 漏洞3: 整数溢出保护不足，在极端情况下可能溢出
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
        // 漏洞1: 没有减少allowance，可以重复使用授权额度
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
        
        // 漏洞2: 任何人都可以mint代币，没有权限控制
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
    
    // 漏洞4: 提取函数存在重入攻击风险
    function withdraw() public {
        uint256 amount = balanceOf[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // 危险：在更新状态前进行外部调用
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
        
        // 状态更新在外部调用之后，存在重入风险
        balanceOf[msg.sender] = 0;
        totalSupply -= amount;
    }
    
    // 接收ETH
    receive() external payable {
        // 简单的ETH存入，1:1兑换代币
        balanceOf[msg.sender] += msg.value;
        totalSupply += msg.value;
        emit Transfer(address(0), msg.sender, msg.value);
    }
}
