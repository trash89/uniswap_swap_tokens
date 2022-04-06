from brownie import accounts, Contract, interface, config, network, TestUniswap


def main():
    active_network = network.show_active()
    testUniswap = TestUniswap.deploy({"from": accounts[0]})
    WETH = config["networks"][active_network]["WETH"]
    DAI = config["networks"][active_network]["DAI"]
    WETH_WHALE = config["networks"][active_network]["WETH_WHALE"]
    DAI_WHALE = config["networks"][active_network]["DAI_WHALE"]
    CALLER = accounts[0]
    TOKEN_A = WETH
    TOKEN_A_WHALE = WETH_WHALE
    TOKEN_B = DAI
    TOKEN_B_WHALE = DAI_WHALE
    TOKEN_A_AMOUNT = 10*10**18  # 10 WETH
    TOKEN_B_AMOUNT = 10*10**18  # 10 DAI

    tokenA = Contract.from_abi("WETH", TOKEN_A, interface.IERC20.abi)
    decimals_A = tokenA.decimals()
    tokenB = Contract.from_abi("DAI", TOKEN_B, interface.IERC20.abi)
    decimals_B = tokenB.decimals()
    pair = interface.IERC20(testUniswap.getPair(
        tokenA.address, tokenB.address))

    print(f"A[0]: {tokenA.balanceOf(accounts[0])/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(accounts[0])/10**decimals_B} {tokenB.symbol()}")
    print(
        f"testUniswap: {tokenA.balanceOf(testUniswap)/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(testUniswap)/10**decimals_B} {tokenB.symbol()}")
    print("Transferring tokens")
    # WETH_WHALE
    print(
        f"balance of WETH_WHALE is {tokenA.balanceOf(TOKEN_A_WHALE)/10**decimals_A} {tokenA.symbol()}")
    # DAI_WHALE
    print(
        f"balance of DAI_WHALE is {tokenB.balanceOf(TOKEN_B_WHALE)/10**decimals_B} {tokenB.symbol()}")

    print(
        f"Transferring {TOKEN_A_AMOUNT/10**decimals_A} {tokenA.symbol()} to accounts[0] from WETH_WHALE")
    tokenA.transfer(CALLER, TOKEN_A_AMOUNT, {"from": TOKEN_A_WHALE})
    print(
        f"Transferring {TOKEN_B_AMOUNT/10**decimals_B} {tokenB.symbol()} to accounts[0] from DAI_WHALE")
    tokenB.transfer(CALLER, TOKEN_B_AMOUNT, {"from": TOKEN_B_WHALE})

    print(f"A[0]: {tokenA.balanceOf(accounts[0])/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(accounts[0])/10**decimals_B} {tokenB.symbol()}")
    print(
        f"testUniswap: {tokenA.balanceOf(testUniswap)/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(testUniswap)/10**decimals_B} {tokenB.symbol()}")

    print(
        "Approving the amounts by accounts[0] in order to be spent by the router")
    tokenA.approve(testUniswap.address, TOKEN_A_AMOUNT, {"from": CALLER})
    tokenB.approve(testUniswap.address, TOKEN_B_AMOUNT, {"from": CALLER})

    tx = testUniswap.getReserves(
        tokenA.address, tokenB.address, {"from": CALLER})
    res0 = tx.return_value[0]
    res1 = tx.return_value[1]
    print(
        f"Reserves into the pool: {res0/10**decimals_A} {tokenA.symbol()}, {res1/10**decimals_B} {tokenB.symbol()}")
    print("*************************")
    print(
        f"Add liquidity {TOKEN_A_AMOUNT/10**decimals_A} {tokenA.symbol()}, {TOKEN_B_AMOUNT/10**decimals_B} {tokenB.symbol()}")
    tx = testUniswap.addLiquidity(
        tokenA.address, tokenB.address, TOKEN_A_AMOUNT, TOKEN_B_AMOUNT, {"from": CALLER})
    tx.wait(1)
    print(
        f"Return: AmountA={tx.return_value[0]/10**decimals_A} {tokenA.symbol()}, AmountB={tx.return_value[1]/10**decimals_B} {tokenA.symbol()}, liquidity={tx.return_value[2]/10**pair.decimals()} {pair.symbol()}({pair.name()}")
    # print(tx.events["Log"]["message"], tx.events["Log"]["val"])
    # print(tx.events["Log"][0]["message"], tx.events["Log"][0]["val"])
    # print(tx.events["Log"][1]["message"], tx.events["Log"][1]["val"])
    # print(tx.events["Log"][2]["message"], tx.events["Log"][2]["val"])

    print(f"A[0]: {tokenA.balanceOf(accounts[0])/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(accounts[0])/10**decimals_B} {tokenB.symbol()}")
    print(
        f"testUniswap: {tokenA.balanceOf(testUniswap)/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(testUniswap)/10**decimals_B} {tokenB.symbol()}")
    print(
        f"liquidity pool: {pair.balanceOf(testUniswap.address)/10**pair.decimals()} {pair.symbol()} ({pair.name()})")
    print("*************************")
    print("Remove liquidity")
    tx = testUniswap.removeLiquidity(
        tokenA.address, tokenB.address, {"from": CALLER, })
    tx.wait(1)
    print(
        f"Returned: AmountA={tx.return_value[0]/10**decimals_A} {tokenA.symbol()}, AmountB={tx.return_value[1]/10**decimals_B} {tokenB.symbol()}")
    # print(tx.events["Log"][0]["message"], tx.events["Log"][0]["val"])
    # print(tx.events["Log"][1]["message"], tx.events["Log"][1]["val"])
    print(f"A[0]: {tokenA.balanceOf(accounts[0])/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(accounts[0])/10**decimals_B} {tokenB.symbol()}")
    print(
        f"testUniswap: {tokenA.balanceOf(testUniswap)/10**decimals_A} {tokenA.symbol()}, {tokenB.balanceOf(testUniswap)/10**decimals_B} {tokenB.symbol()}")
    print(
        f"liquidity pool: {pair.balanceOf(testUniswap.address)/10**pair.decimals()} {pair.symbol()} ({pair.name()})")
    print("--------------------------------------------------------------")
