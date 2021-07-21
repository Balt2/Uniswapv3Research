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
			amountIn = self.sqrtPriceMath.getAmount0Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, True) if zeroForOne else self.sqrtPriceMath.getAmount1Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, True)

			if amountRemainingLessFee > amountIn:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.sqrtPriceMath.getNextSqrtPriceFromInput(sqrtRatioCurrent, liquidity, amountRemainingLessFee, zeroForOne)
		else:
			amountOut = self.sqrtPriceMath.getAmount1Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, False) if zeroForOne else self.sqrtPriceMath.getAmount0Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, False)
			if amountRemaininig * -1 > amountOut:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.sqrtPriceMath.getNextSqrtPriceFromOutput(sqrtRatioCurrent, liquidity, amountRemaininig*-1, zeroForOne)

		maximum = (sqrtRatioTarget == sqrtRatioNextX96) 

		if zeroForOne:
			if not (maximum and exactIn):
				amountIn = self.sqrtPriceMath.getAmount0Delta(sqrtRatioNextX96, sqrtRatioCurrent, liquidity, True)
			if not (maximum and (not exactIn)):
				amountOut = self.sqrtPriceMath.getAmount1Delta(sqrtRatioNextX96, sqrtRatioCurrent, liquidity, False)
		else:
			if not (maximum and exactIn):
				amountIn = self.sqrtPriceMath.getAmount1Delta(sqrtRatioCurrent, sqrtRatioNextX96, liquidity, True)
			if not (maximum and (not exactIn)):
				amountOut = self.sqrtPriceMath.getAmount1Delta(sqrtRatioCurrent, sqrtRatioNextX96, liquidity, False)


		if (not exactIn and amountOut > amountRemaininig*-1):
			amountOut = amountRemaininig * -1			
		
		if (exactIn and not (sqrtRatioNextX96 == sqrtRatioTarget)):
			feeAmount = amountRemaininig - amountIn
		else:
			feeAmount = self.SqrtPriceMath.mulDivRoundingUp(amountIn, feePips, constants.MAX_FEE - feePips)

		return (sqrtRatioNextX96, amountIn, amountOut, feeAmount)

	


	def swap(self, zeroForOne, amountSpecified, sqrtPriceLimitX96 = "BEN"):
		if sqrtPriceLimitX96 == "BEN":
			sqrtPriceLimitX96 = constants.MIN_SQRT_RATIO + 1 if zeroForOne else constants.MAX_SQRT_RATIO - 1

  		#TODO: add invariant

		exactInput = (amountSpecified >= 0)

		#STATE
		stateAmountSpecifiedRemaining = amountSpecified
		stateAmountCalculated = 0
		stateSqrtPriceX96 = self.sqrtRatioX96
		stateTick = self.tickCurrent
		stateLiquidity = self.liquidity


		while stateAmountSpecifiedRemaining != 0 and stateSqrtPriceX96 != sqrtPriceLimitX96:
			stepSqrtPriceStartX96 = stateSqrtPriceX96

			stepTickNext, stepInitialized = self.nextInitTickWithinOneWord(stateTick, zeroForOne, self.tickSpacing)

			if stepTickNext < constants.MIN_TICK:
				stepTickNext = constants.MIN_TICK
			elif stepTickNext > constants.MAX_TICK:
				stepTickNext = constants.MAX_TICK

			stepSqrtPriceNextX96 = self.sqrtPriceMath.sqrtRatioAtTick(stepTickNext)

			target = 0
			if zeroForOne:
				if stepSqrtPriceNextX96 < sqrtPriceLimitX96:
					target = sqrtPriceLimitX96
				else:
					target = stepSqrtPriceNextX96
			else:
				if stepSqrtPriceNextX96 > sqrtPriceLimitX96:
					target = sqrtPriceLimitX96
				else:
					target = stepSqrtPriceNextX96

			stateSqrtPriceX96, stepAmountIn, stepAmountOut, stepFeeAmount = self.computeSwapStep(stateSqrtPriceX96, target, stateLiquidity, stateAmountSpecifiedRemaining, self.feeTeir)

			if exactInput:
				stateAmountSpecifiedRemaining = stateAmountSpecifiedRemaining - (stepAmountIn + stepFeeAmount )
				stateAmountCalculated = stateAmountCalculated - stepAmountOut
			else:
				stateAmountSpecifiedRemaining += stepAmountOut
				stateAmountCalculated += (stepAmountIn + stepFeeAmount)

			if stateSqrtPriceX96 == stepSqrtPriceNextX96:
				if stepInitialized:
					liquidityNet = (tickDataProvider.getTick(stepTickNext)).liquidityNet
					if zeroForOne:
						liquidityNet = liquidityNet * -1
					stateLiquidity = self.sqrtPriceMath.addDelta(stateLiquidity, liquidityNet)

				stateTick = stepTickNext - 1 if zeroForOne else stepTickNext
			elif stateSqrtPriceX96 != stepSqrtPriceStartX96:
				stateTick = self.sqrtPriceMath.getTickAtSqrtRatio(stateSqrtPriceX96)

		return stateAmountCalculated, stateSqrtPriceX96, stateLiquidity, stateTick


			


	def getOutputAmount(self, inputAmount, sqrtPriceLimitX96):
		zeroForOne = inputAmount.currency.address == self.token0

		outputAmount, sqrtRatioX96, liquidity, tickCurrent = self.swap(token0ForToken1, inputAmount.quotient(), sqrtPriceLimitX96)

		outputToken = self.token1 if zeroForOne else self.token0

		return (CurrencyAmount(outputToken, outputAmount*-1), Pool(self.token0, self.token1, self.feeTeir, sqrtRatioX96, liquidity, tickCurrent, self.tickDataProvider.ticks, self.address, self.tickSpacing ))



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







