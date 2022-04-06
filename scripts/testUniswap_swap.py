from brownie import accounts, Contract, interface, config, network, TestUniswap


def main():
    active_network = network.show_active()
    WHALE = config["networks"][active_network]["WBTC_WHALE"]
    AMOUNT_IN = 1000  # swap 1000 WBTC to DAI
    AMOUNT_OUT_MIN = 1
    TOKEN_IN = config["networks"][active_network]["WBTC"]
    TOKEN_OUT = config["networks"][active_network]["DAI"]
    TO = accounts[0]

    tokenIn = Contract.from_abi("WBTC", TOKEN_IN, interface.IERC20.abi)
    decimals_In = tokenIn.decimals()
    tokenOut = Contract.from_abi("DAI", TOKEN_OUT, interface.IERC20.abi)
    decimals_Out = tokenOut.decimals()
    testUniswap = TestUniswap.deploy({"from": accounts[0]})
    tokenIn.approve(testUniswap.address, AMOUNT_IN, {"from": WHALE})

    amount_out_min = testUniswap.getAmountOutMin(tokenIn.address, tokenOut.address,
                                                 AMOUNT_IN, {"from": WHALE})
    print(
        f"Amount out min : {amount_out_min/10**decimals_Out} {tokenOut.symbol()}")

    print(
        f"Intial: {tokenIn.balanceOf(TO)/10**decimals_In} {tokenIn.symbol()}, {tokenOut.balanceOf(TO)/10**decimals_Out} {tokenOut.symbol()}")

    testUniswap.swap(tokenIn.address, tokenOut.address,
                     AMOUNT_IN, AMOUNT_OUT_MIN, TO, {"from": WHALE})
    print(
        f"Swapped {AMOUNT_IN} {tokenIn.symbol()} to {tokenOut.balanceOf(TO)/10**decimals_Out} {tokenOut.symbol()}")
    print(
        f"Final: {tokenIn.balanceOf(TO)/10**decimals_In} {tokenIn.symbol()}, {tokenOut.balanceOf(TO)/10**decimals_Out} {tokenOut.symbol()}")

    print("--------------------------------------------------------------")
