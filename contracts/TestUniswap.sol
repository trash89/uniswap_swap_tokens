// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "@Uniswap/v2-core/contracts/interfaces/IERC20.sol";
import "@Uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
import "@Uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "@Uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router01.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract TestUniswap {
    using SafeMath for uint256;
    address private constant UNISWAP_V2_ROUTER =
        0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address private constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private constant FACTORY =
        0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f;
    event Log(string message, uint256 val);

    function swap(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn,
        uint256 _amountOutMin,
        address _to
    ) external {
        IERC20(_tokenIn).transferFrom(msg.sender, address(this), _amountIn);
        IERC20(_tokenIn).approve(UNISWAP_V2_ROUTER, _amountIn);

        address[] memory path;
        if (_tokenIn == WETH || _tokenOut == WETH) {
            path = new address[](2);
            path[0] = _tokenIn;
            path[1] = _tokenOut;
        } else {
            path = new address[](3);
            path[0] = _tokenIn;
            path[1] = WETH;
            path[2] = _tokenOut;
        }

        IUniswapV2Router01(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amountIn,
            _amountOutMin,
            path,
            _to,
            block.timestamp
        );
    }

    function getAmountOutMin(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn
    ) external view returns (uint256) {
        address[] memory path;
        if (_tokenIn == WETH || _tokenOut == WETH) {
            path = new address[](2);
            path[0] = _tokenIn;
            path[1] = _tokenOut;
        } else {
            path = new address[](3);
            path[0] = _tokenIn;
            path[1] = WETH;
            path[2] = _tokenOut;
        }

        // same length as path
        uint256[] memory amountOutMins = IUniswapV2Router01(UNISWAP_V2_ROUTER)
            .getAmountsOut(_amountIn, path);

        return amountOutMins[path.length - 1];
    }

    function addLiquidity(
        address _tokenA,
        address _tokenB,
        uint256 _amountA,
        uint256 _amountB
    )
        external
        returns (
            uint256,
            uint256,
            uint256
        )
    {
        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);
        IERC20(_tokenB).transferFrom(msg.sender, address(this), _amountB);

        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER, _amountA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER, _amountB);

        (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        ) = IUniswapV2Router01(UNISWAP_V2_ROUTER).addLiquidity(
                _tokenA,
                _tokenB,
                _amountA,
                _amountB,
                1,
                1,
                address(this),
                block.timestamp
            );
        emit Log("amountA", amountA);
        emit Log("amountB", amountB);
        emit Log("liquidity", liquidity);
        return (amountA, amountB, liquidity);
    }

    function removeLiquidity(address _tokenA, address _tokenB)
        external
        returns (uint256, uint256)
    {
        address pair = IUniswapV2Factory(FACTORY).getPair(_tokenA, _tokenB);

        uint256 liquidity = IERC20(pair).balanceOf(address(this));
        IERC20(pair).approve(UNISWAP_V2_ROUTER, liquidity);

        (uint256 amountA, uint256 amountB) = IUniswapV2Router01(
            UNISWAP_V2_ROUTER
        ).removeLiquidity(
                _tokenA,
                _tokenB,
                liquidity,
                1,
                1,
                address(this),
                block.timestamp
            );
        emit Log("amountA", amountA);
        emit Log("amountB", amountB);
        return (amountA, amountB);
    }

    function getReserves(address _tokenA, address _tokenB)
        external
        returns (uint256, uint256)
    {
        address pair = IUniswapV2Factory(FACTORY).getPair(_tokenA, _tokenB);
        (uint256 reserve0, uint256 reserve1, ) = IUniswapV2Pair(pair)
            .getReserves();
        return (reserve0, reserve1);
    }

    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
        // else z = 0 (default value)
    }

    /*
  s = optimal swap amount
  r = amount of reserve for token a
  a = amount of token a the user currently has (not added to reserve yet)
  f = swap fee percent
  s = (sqrt(((2 - f)r)^2 + 4(1 - f)ar) - (2 - f)r) / (2(1 - f))
  */
    function getSwapAmount(uint256 r, uint256 a) public pure returns (uint256) {
        return
            (sqrt(r.mul(r.mul(3988009) + a.mul(3988000))).sub(r.mul(1997))) /
            1994;
    }

    /* optimal one-sided supply
  1. swap optimal amount from token A to token B
  2. add liquidity
  */
    function zap(
        address _tokenA,
        address _tokenB,
        uint256 _amountA
    ) external {
        require(_tokenA == WETH || _tokenB == WETH, "!weth");

        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);

        address pair = IUniswapV2Factory(FACTORY).getPair(_tokenA, _tokenB);
        (uint256 reserve0, uint256 reserve1, ) = IUniswapV2Pair(pair)
            .getReserves();

        uint256 swapAmount;
        if (IUniswapV2Pair(pair).token0() == _tokenA) {
            // swap from token0 to token1
            swapAmount = getSwapAmount(reserve0, _amountA);
        } else {
            // swap from token1 to token0
            swapAmount = getSwapAmount(reserve1, _amountA);
        }

        _swap(_tokenA, _tokenB, swapAmount);
        _addLiquidity(_tokenA, _tokenB);
    }

    /* sub-optimal one-sided supply
  1. swap half of token A to token B
  2. add liquidity
  */
    function subOptimalZap(
        address _tokenA,
        address _tokenB,
        uint256 _amountA
    ) external {
        IERC20(_tokenA).transferFrom(msg.sender, address(this), _amountA);

        _swap(_tokenA, _tokenB, _amountA.div(2));
        _addLiquidity(_tokenA, _tokenB);
    }

    function _swap(
        address _from,
        address _to,
        uint256 _amount
    ) internal {
        IERC20(_from).approve(UNISWAP_V2_ROUTER, _amount);

        address[] memory path = new address[](2);
        path = new address[](2);
        path[0] = _from;
        path[1] = _to;

        IUniswapV2Router01(UNISWAP_V2_ROUTER).swapExactTokensForTokens(
            _amount,
            1,
            path,
            address(this),
            block.timestamp
        );
    }

    function _addLiquidity(address _tokenA, address _tokenB) internal {
        uint256 balA = IERC20(_tokenA).balanceOf(address(this));
        uint256 balB = IERC20(_tokenB).balanceOf(address(this));
        IERC20(_tokenA).approve(UNISWAP_V2_ROUTER, balA);
        IERC20(_tokenB).approve(UNISWAP_V2_ROUTER, balB);

        IUniswapV2Router01(UNISWAP_V2_ROUTER).addLiquidity(
            _tokenA,
            _tokenB,
            balA,
            balB,
            0,
            0,
            address(this),
            block.timestamp
        );
    }

    function getPair(address _tokenA, address _tokenB)
        external
        view
        returns (address)
    {
        return IUniswapV2Factory(FACTORY).getPair(_tokenA, _tokenB);
    }
}
