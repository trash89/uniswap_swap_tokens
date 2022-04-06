from brownie import accounts, Contract, interface, config, network, TestUniswap


def main():
    active_network = network.show_active()
    testUniswap = TestUniswap.deploy({"from": accounts[0]})

    WETH = config["networks"][active_network]["WETH"]
    DAI = config["networks"][active_network]["DAI"]
    USDC = config["networks"][active_network]["USDC"]

    WETH_WHALE = config["networks"][active_network]["WETH_WHALE"]
    DAI_WHALE = config["networks"][active_network]["DAI_WHALE"]
    USDC_WHALE = config["networks"][active_network]["USDC_WHALE"]
    WHALE = USDC_WHALE
    TOKEN_BORROW = USDC
    token = Contract.from_abi("USDC", TOKEN_BORROW, interface.IERC20.abi)
    DECIMALS = token.decimals()
    FUND_AMOUNT = 2000*10**DECIMALS  # 2000 USDC
    BORROW_AMOUNT = 1000*10**DECIMALS  # borrow 1000 USDC

    print(
        f"Initial, testUniswap : {token.balanceOf(testUniswap)/10**DECIMALS} {token.symbol()}")

    # send enough token to cover fee
    bal = token.balanceOf(WHALE)
    print(f"Balance of WHALE is {bal/10**DECIMALS} {token.symbol()}")
    assert bal > FUND_AMOUNT
    print(
        f"Funding the testUniswap contract with {FUND_AMOUNT/10**DECIMALS} {token.symbol()}")
    token.transfer(testUniswap.address, FUND_AMOUNT, {"from": WHALE})
    print(
        f"After funding, testUniswap : {token.balanceOf(testUniswap)/10**DECIMALS} {token.symbol()}")

    print(
        f"Flashswap {BORROW_AMOUNT/10**DECIMALS} {token.symbol()} from WHALE")
    tx = testUniswap.testFlashSwap(
        token.address, BORROW_AMOUNT, {"from": WHALE, })
    tx.wait(1)
    print(
        f"After Flashswap, testUniswap : {token.balanceOf(testUniswap)/10**DECIMALS} {token.symbol()}")
    print(tx.events["Log"][0]["message"], tx.events["Log"][0]["val"])
    print(tx.events["Log"][1]["message"], tx.events["Log"][1]["val"])
    print(tx.events["Log"][2]["message"], tx.events["Log"][2]["val"])
    print(tx.events["Log"][3]["message"], tx.events["Log"][3]["val"])
    print(tx.events["Log"][4]["message"], tx.events["Log"][4]["val"])
