"""
形式化规范定义 - 定义智能合约应该满足的不变量和前后置条件
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Invariant:
    """不变量定义"""
    name: str
    description: str
    condition: str  # Solidity条件表达式
    violation_check: str  # 违反检测的断言


@dataclass
class PreCondition:
    """前置条件定义"""
    function_name: str
    condition: str
    description: str


@dataclass
class PostCondition:
    """后置条件定义"""
    function_name: str
    condition: str
    description: str


class FormalSpecGenerator:
    """形式化规范生成器"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.invariants = self._define_erc20_invariants()
        self.pre_conditions = self._define_erc20_pre_conditions()
        self.post_conditions = self._define_erc20_post_conditions()
    
    def _define_erc20_invariants(self) -> List[Invariant]:
        """定义ERC20合约的不变量"""
        return [
            Invariant(
                name="total_supply_conservation",
                description="代币总供应量应该等于所有账户余额之和",
                condition="token.totalSupply() == _sumAllBalances()",
                violation_check="assertEq(token.totalSupply(), _sumAllBalances(), 'Total supply invariant violated')"
            ),
            Invariant(
                name="balance_non_negative",
                description="所有账户余额必须非负",
                condition="token.balanceOf(account) >= 0",
                violation_check="assertTrue(token.balanceOf(attacker) >= 0 && token.balanceOf(victim) >= 0, 'Balance non-negative invariant violated')"
            ),
            Invariant(
                name="allowance_consistency",
                description="授权额度不应该在未经授权的情况下增加",
                condition="allowance can only decrease or be reset",
                violation_check="assertTrue(token.allowance(victim, attacker) <= initialAllowance, 'Allowance consistency invariant violated')"
            ),
            Invariant(
                name="unauthorized_mint_prevention",
                description="只有授权用户才能铸造代币",
                condition="mint operations require proper authorization",
                violation_check="assertTrue(token.balanceOf(attacker) == 0 || attackerWasAuthorized, 'Unauthorized mint prevention invariant violated')"
            ),
            Invariant(
                name="contract_eth_balance_safety",
                description="合约ETH余额不应该被未授权提取",
                condition="contract ETH balance should not decrease without authorization",
                violation_check="assertTrue(address(token).balance >= expectedMinBalance, 'Contract ETH balance safety invariant violated')"
            )
        ]
    
    def _define_erc20_pre_conditions(self) -> List[PreCondition]:
        """定义ERC20函数的前置条件"""
        return [
            PreCondition(
                function_name="transfer",
                condition="balanceOf[msg.sender] >= amount",
                description="转账前发送者余额必须足够"
            ),
            PreCondition(
                function_name="transferFrom", 
                condition="balanceOf[from] >= amount && allowance[from][msg.sender] >= amount",
                description="授权转账前余额和授权额度必须足够"
            ),
            PreCondition(
                function_name="withdraw",
                condition="balanceOf[msg.sender] > 0",
                description="提取前必须有代币余额"
            )
        ]
    
    def _define_erc20_post_conditions(self) -> List[PostCondition]:
        """定义ERC20函数的后置条件"""
        return [
            PostCondition(
                function_name="transfer",
                condition="balanceOf[to] == old(balanceOf[to]) + amount && balanceOf[from] == old(balanceOf[from]) - amount",
                description="转账后余额应该正确更新"
            ),
            PostCondition(
                function_name="transferFrom",
                condition="allowance[from][msg.sender] == old(allowance[from][msg.sender]) - amount",
                description="授权转账后授权额度应该减少"
            ),
            PostCondition(
                function_name="mint",
                condition="totalSupply == old(totalSupply) + amount && balanceOf[to] == old(balanceOf[to]) + amount",
                description="铸币后总供应量和目标余额应该增加"
            ),
            PostCondition(
                function_name="withdraw",
                condition="balanceOf[msg.sender] == 0 && address(this).balance == old(address(this).balance) - amount",
                description="提取后用户余额清零，合约ETH减少"
            )
        ]
    
    def get_invariants_for_test(self, vulnerability_type: str = None) -> List[Invariant]:
        """获取用于测试的不变量"""
        if vulnerability_type == "unauthorized_mint":
            return [inv for inv in self.invariants if inv.name in ["unauthorized_mint_prevention", "total_supply_conservation"]]
        elif vulnerability_type == "allowance_bypass":
            return [inv for inv in self.invariants if inv.name in ["allowance_consistency", "balance_non_negative"]]
        elif vulnerability_type == "reentrancy":
            return [inv for inv in self.invariants if inv.name in ["contract_eth_balance_safety", "balance_non_negative"]]
        else:
            return self.invariants[:3]  # 返回前3个最重要的不变量


