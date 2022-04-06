from brownie import accounts, Contract, interface, config, network, TestUniswap


def main():
    active_network = network.show_active()
    testUniswap = TestUniswap.deploy({"from": accounts[0]})
    WETH = config["networks"][active_network]["WETH"]
    DAI = config["networks"][active_network]["DAI"]
    DAI_WHALE = config["networks"][active_network]["DAI_WHALE"]
    WHALE = DAI_WHALE
    AMOUNT = 1000*10**18
    fromToken = Contract.from_abi("DAI", DAI, interface.IERC20.abi)
    toToken = Contract.from_abi("WETH", WETH, interface.IERC20.abi)

    pair = interface.IERC20(testUniswap.getPair(
        fromToken.address, toToken.address))
    fromToken.approve(testUniswap.address, AMOUNT, {"from": WHALE})

    print("SubOptimal swap")
    print("Before calling subOptimalZap():")
    print(
        f"liquidity pool: {pair.balanceOf(testUniswap.address)/10**pair.decimals()} {pair.symbol()} ({pair.name()})")
    print(
        f"fromToken: {fromToken.balanceOf(testUniswap.address)/10**fromToken.decimals()} {fromToken.symbol()}")
    print(
        f"toToken: {toToken.balanceOf(testUniswap.address)/10**toToken.decimals()} {toToken.symbol()}")
    tx = testUniswap.subOptimalZap(
        fromToken.address, toToken.address, AMOUNT, {"from": WHALE, })
    tx.wait(1)
    print("After calling subOptimalZap():")
    print(
        f"liquidity pool: {pair.balanceOf(testUniswap.address)/10**pair.decimals()} {pair.symbol()} ({pair.name()})")
    print(
        f"fromToken: {fromToken.balanceOf(testUniswap.address)/10**fromToken.decimals()} {fromToken.symbol()}")
    print(
        f"toToken: {toToken.balanceOf(testUniswap.address)/10**toToken.decimals()} {toToken.symbol()}")
    print("--------------------------------------------------------------")
