import math
import constants
import SqrtPriceMath
import TickList

class Tick:
	def __init__(self, liquidityActive, tickIdx, liquidityNet, liquidityGross, token0, token1):
		self.liquidityActive = liquidityActive
		self.liquidityNet = liquidityNet
		self.tickIdx = int(tickIdx)
		self.liquidityGross = liquidityGross
		self.price0 = (10 ** (token1.decimals - token0.decimals)) / (1.0001 ** (tickIdx))
		self.price1  = (1.0001 ** tickIdx) * (10 ** (token0.decimals - token1.decimals))
		#print(token0.decimals)
		#print(token1.decimals)

	def setLiquidityGross(self, l):
		self.liquidityGross = l

	def setLiquidityNet(self, l):
		self.liquidityNet = l

	def setLiquidityActive(self, l):
		self.liquidityActive = l

class Token:
	def __init__(self, address, symbol, decimals):
		self.address = address
		self.symbol = symbol
		self.decimals = decimals

	def sortsBefore(self, other):
		return this.address.lower() < other.address.lower()

	def equals(self, other):
		return this.address == other.address

class Transaction:
	def __init__(self, blockNumber, timeStamp, gasUsed):
		self.blockNumber = blockNumber
		self.timeStamp = timeStamp
		self.gasUsed = gasUsed

class Swap:
	def __init__(self, token0, token1, amountUSD, amountToken0, amountToken1, gasPrice, tick):
		self.token0 = token0
		self.token1 = token1
		self.amountUSD = amountUSD
		self.amountToken0 = amountToken0
		self.amountToken1 = amountToken1
		self.gasPrice = gasPrice
		self.tick = tick

class Block:
	def __init__(self, swap, blockNumber, timeStamp): #AverageGas should come from the avreage gas on the whole block
		self.blockNumber = blockNumber
		self.totalUSD = swap.amountUSD
		self.token0Total = swap.amountToken0
		self.token1Total = swap.amountToken1
		self.timeStamp = timeStamp
		self.averageGas = swap.gasPrice
		self.swaps = [swap]

	def addSwap(self, swap):
		self.totalUSD += swap.amountUSD
		self.token0Total += swap.amountToken0
		self.token1Total += swap.amountToken1

		gasSum = 0
		for s in self.swaps:
			gasSum += s.gasPrice

		self.averageGas = float(gasSum /len(self.swaps))

class Pool:
	def __init__(self, token0, token1, feeTeir, sqrtRatioX96,liquidity, tick, ticks, address, tickSpacing):
		self.address = address
		self.feeTeir = feeTeir
		self.token0 = token0
		self.token1 = token1
		self.liquidity = liquidity
		self.sqrtRatioX96 = sqrtRatioX96
		self.tickCurrent = tick
		self.tickDataProvider = TickList(ticks, tickSpacing)
		self.tickCurrentSqrtRatioX96 = self.sqrtRatioAtTick(tick)
		self.nextTickSqrtRatioX96 = self.sqrtRatioAtTick(tick + 1)
		self.tickSpacing = tickSpacing
		self.sqrtPriceMath = SqrtPriceMath()


	def getToken0Price(self):
		return Price(self.token0, self.token1, constants.q192, self.sqrtRatioX96 * self.sqrtRatioX96)

	def getToken1Price(self):
		return Price(self.token1, self.token0, self.sqrtRatioX96 * self.sqrtRatio, constants.q192)

	def priceOf(self, token):
		if token.address == self.token0.address:
			return self.token0
		else:
			return self.token1
		#TODO Check if token is not token0 or token1

	def computeSwapStep(self, sqrtRatioCurrent, sqrtRatioTarget, liquidity, amountRemaininig, feePips):
		zeroForOne = (sqrtRatioCurrent >= sqrtRatioTarget)
		exactIn = (amountRemaininig >= 0)

		if exactIn:
			amountRemainingLessFee = (amountRemaininig * (constants.MAX_FEE - feePips) / constants.MAX_FEE)
			amountIn = self.getAmount0Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, True) if zeroForOne else self.getAmount1Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, True)

			if amountRemainingLessFee > amountIn:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.getNextSqrtPriceFromInput(sqrtRatioCurrent, liquidity, amountRemainingLessFee, zeroForOne)
		else:
			amountOut = self.getAmount1Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, False) if zeroForOne else self.getAmount0Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, False)
			if amountRemaininig * -1 > amountOut:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.getNextSqrtPriceFromOutput(sqrtRatioCurrent, liquidity, amountRemaininig*-1, zeroForOne)


	def swap(self, zeroForOne, amountSpecified, sqrtPriceLimit = "BEN"):
		if sqrtPriceLimit == "BEN":
			sqrtPriceLimit = constants.MIN_SQRT_RATIO + 1 if zeroForOne else constants.MAX_SQRT_RATIO - 1

  		#TODO: add invariant

		exactInput = (amountSpecified >= 0)

		#STATE
		stateAmountSpecifiedRemaining = amountSpecified
		stateAmountCalculated = 0
		stateSqrtPriceX96 = self.sqrtRatioX96
		stateTick = self.tickCurrent
		stateLiquidity = self.liquidity


		while stateAmountSpecifiedRemaining != 0 and stateSqrtPriceX96 != sqrtPriceLimitX96:
			step = StepComputations()
			step.setSqrtPriceStart(stateSqrtPriceX96)

			tickNext, initialized = self.nextInitTickWithinOneWord(stateTick, zeroForOne, self.tickSpacing)

			if tickNext < constants.MIN_TICK:
				tickNext = constants.MIN_TICK
			elif tickNext > constants.MAX_TICK:
				tickNext = constants.MAX_TICK

			step.setTickNext(tickNext)
			step.setInit(initialized)

			step.setSqrtPriceNext(self.sqrtPriceMath.sqrtRatioAtTick(tickNext))
			sqrtPriceX96, amountIn, amountOut, feeAmount = 


	def getOutputAmount(self, inputAmount, sqrtPriceLimitX96):
		zeroForOne = inputAmount.currency.address == self.token0

		outputAmount, sqrtRatioX96, liquidity, tickCurrent = self.swap(token0ForToken1, inputAmount.quotient(), sqrtPriceLimit)

		outputToken = self.token1 if zeroForOne else self.token0

		return CurrencyAmount.fromRawAmount(outputToken, outputAmount*-1)



class Price:
	def __init__(self, tBase, tQuote, denominator, numerator):
		self.baseCurrency = tBase
		self.quoteCurrency = tQuote
		self.denominator = denominator
		self.numerator = numerator
		self.scaler = Fraction(10 ** baseCurrency.decimals, 10 ** quoteCurrency.decimals)

	def invert(self):
		return Price(self.quoteCurrency, self.baseCurrency, self.denominator, self.numerator)

	def multply(self, other):
		num = self.numerator * other.numerator
		den = self.denominator * other.denominator
		return Price(self.baseCurrency, self.quoteCurrency, den, num) 

class CurrencyAmount:
	def __init__(self, token, numerator, denominator=1):
		self.currency = token
		self.decimalScale = 10 ** token.decimals
		self.price = Fraction(numerator, denominator)

	def fromRawAmount(self, currency, rawAmount):
		return CurrencyAmount(currency, rawAmount)

class Fraction:
	def __init__(self, numerator, denominator):
		self.numerator = numerator
		self.denominator = denominator

	def quotient(self):
		return self.numerator / self.denominator

	def multiply(self, other):
		return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)

	def divide(self, other):
		return Fraction(self.numerator * other.denominator, self.denominator * other.numerator)

	def invert(self):
		return Fraction(self.denominator, self.numerator)


class StepComputations:
	def __init__(self, sqrtPriceStartX96=0, tickNext=0, initialized=True, sqrtPriceNextX96=0, amountIn=0, amountOut=0, feeAmount=0):
		self.sqrtPriceStartX96 = sqrtPriceStartX96
		self.tickNext = tickNext
		self.initialized = initialized
		self.sqrtPriceNextX96 = sqrtPriceNextX96
		self.amountIn = amountIn
		self.amountOut = amountOut
		self.feeAmount = feeAmount

	def setSqrtPriceStart(self, sqrtPrice):
		self.sqrtPriceNextX96 = sqrtPrice

	def setTickNext(self, tickNext):
		self.tickNext = tickNext

	def setInit(self, init):
		self.initialized = init

	def setSqrtPriceNext(self, sqrtPriceNext):
		self.sqrtPriceNextX96 = sqrtPriceNext







