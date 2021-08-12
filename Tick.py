import math
import constants
from SqrtPriceMath import *
from TickList import *
import sys
import matplotlib.pyplot as plt
#import testGraph


class Tick:
	def __init__(self, liquidityActive, tickIdx, liquidityNet, liquidityGross, token0, token1):
		self.liquidityActive = liquidityActive
		self.liquidityNet = liquidityNet
		self.tickIdx = int(tickIdx)
		self.liquidityGross = liquidityGross
		self.price0 = (10 ** (token1.decimals - token0.decimals)) / (1.0001 ** (tickIdx))
		self.price1 = (1.0001 ** tickIdx) * (10 ** (token0.decimals - token1.decimals))
		#print(token0.decimals)
		#print(token1.decimals)
		self.amount = 0
		self.amount0 = 0
		self.amount1 = 0
		self.amountUSD = 0

	def setLiquidityGross(self, l):
		self.liquidityGross = l

	def setLiquidityNet(self, l):
		self.liquidityNet = l

	def setLiquidityActive(self, l):
		self.liquidityActive = l

	def setTvl(self, val, token0Bool):
		if token0Bool:
			self.tvlToken0 = val
		else:
			self.tvlToken1 = val

	def updateAmount(self, amount):
		self.amount += amount

	def updateAmount0(self, amount):
		self.amount0 += amount

	def updateAmount1(self, amount):
		self.amount1 += amount

	def updateAmountUSD(self, amount):
		self.amountUSD += amount

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
	def __init__(self, token0, token1, amountUSD, amountToken0, amountToken1, gasPrice, tick, blockNumber = 0):
		self.token0 = token0
		self.token1 = token1
		self.amountUSD = amountUSD
		self.amountToken0 = amountToken0
		self.amountToken1 = amountToken1
		self.gasPrice = gasPrice
		self.tick = tick

		#Use for V2
		self.blockNumber = blockNumber 

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
		self.sqrtPriceMath = SqrtPriceMath()
		self.address = address
		self.feeTeir = feeTeir
		self.token0 = token0
		self.token1 = token1
		self.liquidity = liquidity
		self.sqrtRatioX96 = sqrtRatioX96
		self.tickCurrent = tick
		self.tickDataProvider = TickList(ticks, tickSpacing)
		self.tickCurrentSqrtRatioX96 = self.sqrtPriceMath.getSqrtRatioAtTick(tick)
		self.nextTickSqrtRatioX96 = self.sqrtPriceMath.getSqrtRatioAtTick(tick + 1)
		self.tickSpacing = tickSpacing
		self.token0Total = 0
		self.token1Total = 0

	def reset(self):
		self.liquidity = 0
		self.sqrtRatioX96 = 0
		self.tickCurrent = 0
		self.tickDataProvider.reset()
		self.tickCurrentSqrtRatioX96 = 0
		self.nextTickSqrtRatioX96 = 0
		self.token0Total = 0
		self.token1Total = 0

	def getToken0Price(self):
		return Price(self.token0, self.token1, constants.q192, self.sqrtRatioX96 * self.sqrtRatioX96)

	def feeTierToBarWidth(self, feeTier, currentPrice):
		feeTierInt = int(feeTier)
		width = abs(currentPrice - currentPrice*(1 + feeTierInt*.000001) )
		return width


	def getToken1Price(self):
		return Price(self.token1, self.token0, self.sqrtRatioX96 * self.sqrtRatio, constants.q192)

	def priceOf(self, token):
		if token.address == self.token0.address:
			return self.token0
		else:
			return self.token1
		#TODO Check if token is not token0 or token1

	def setSqrtRatioX96(self, ratio):
		self.sqrtRatioX96 = ratio

	def setTickList(self, tickList):
		self.tickDataProvider = tickList

	def setTickCurrent(self, tick):
		activeTickIdx = (tick // self.tickSpacing) *  self.tickSpacing
		self.tickCurrent = tick

	def setLiquidity(self, liq):
		self.liquidity = liq

	def addLiquidity(self, liq):
		self.liquidity += liq
	def computeSwapStep(self, sqrtRatioCurrent, sqrtRatioTarget, liquidity, amountRemaininig, feePips, zeroForOne):
		#print("amountRemaininig: ", amountRemaininig)
		zeroForOne = (sqrtRatioCurrent >= sqrtRatioTarget)
		#print("zeroForOne: ", zeroForOne)
		exactIn = (amountRemaininig >= 0)
		liquidity = int(liquidity)
		if exactIn:
			amountRemainingLessFee = int(( (amountRemaininig * (constants.MAX_FEE - feePips)) // constants.MAX_FEE))
			#print("amountRemainingLessFee: ", amountRemainingLessFee)
			#print("LIQUIDITY: ", liquidity)
			amountIn = self.sqrtPriceMath.getAmount0Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, True) if zeroForOne else self.sqrtPriceMath.getAmount1Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, True)
			print("Exact In amount0Delta: ", amountIn)
			if amountRemainingLessFee >= amountIn:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.sqrtPriceMath.getNextSqrtPriceFromInput(sqrtRatioCurrent, liquidity, amountRemainingLessFee, zeroForOne)
			#print("sqrtRatioNextX96: ", sqrtRatioNextX96)
		else:
			amountOut = self.sqrtPriceMath.getAmount1Delta(sqrtRatioTarget, sqrtRatioCurrent, liquidity, False) if zeroForOne else self.sqrtPriceMath.getAmount0Delta(sqrtRatioCurrent, sqrtRatioTarget, liquidity, False)
			#print("AMOUNT OUT Ben: ", amountOut)
			if amountRemaininig * -1 >= amountOut:
				sqrtRatioNextX96 = sqrtRatioTarget
			else:
				sqrtRatioNextX96 = self.sqrtPriceMath.getNextSqrtPriceFromOutput(sqrtRatioCurrent, liquidity, amountRemaininig*-1, zeroForOne)

		maximum = (sqrtRatioTarget == sqrtRatioNextX96) 

		if zeroForOne:
			if not (maximum and exactIn):
				amountIn = self.sqrtPriceMath.getAmount0Delta(sqrtRatioNextX96, sqrtRatioCurrent, liquidity, True)
			if not (maximum and (not exactIn)):
				amountOut = self.sqrtPriceMath.getAmount1Delta(sqrtRatioNextX96, sqrtRatioCurrent, liquidity, False)
				#print("AMOUNT OUT MAX: ", amountOut)
		else:
			if not (maximum and exactIn):
				amountIn = self.sqrtPriceMath.getAmount1Delta(sqrtRatioCurrent, sqrtRatioNextX96, liquidity, True)
				print("!zeroForOne In amount1Delta: ", amountIn)
			if not (maximum and (not exactIn)):
				amountOut = self.sqrtPriceMath.getAmount0Delta(sqrtRatioCurrent, sqrtRatioNextX96, liquidity, False)
				#print("AMOUNT OUT Dan: ", amountOut)


		if (not exactIn and amountOut > amountRemaininig*-1):
			amountOut = amountRemaininig * -1			
		
		if (exactIn and not (sqrtRatioNextX96 == sqrtRatioTarget)):
			feeAmount = amountRemaininig - amountIn
		else:
			feeAmount = self.sqrtPriceMath.mulDivRoundingUp(amountIn, feePips, constants.MAX_FEE - feePips)

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
		#print("State liquidity Initiali: ", stateLiquidity)
		while stateAmountSpecifiedRemaining >= 1 and stateSqrtPriceX96 != sqrtPriceLimitX96:
			
			stepSqrtPriceStartX96 = stateSqrtPriceX96

			stepTickNext, stepInitialized = self.tickDataProvider.nextInitializedTickWithinOneWord(stateTick, zeroForOne)
			if stepTickNext < constants.MIN_TICK:
				stepTickNext = constants.MIN_TICK
			elif stepTickNext > constants.MAX_TICK:
				stepTickNext = constants.MAX_TICK

			stepSqrtPriceNextX96 = self.sqrtPriceMath.getSqrtRatioAtTick(stepTickNext)
			target = 0
			if zeroForOne:
				if stepSqrtPriceNextX96 < sqrtPriceLimitX96:
					target = sqrtPriceLimitX96
				else:
					#At the moment the code always goes here
					target = stepSqrtPriceNextX96
			else:
				if stepSqrtPriceNextX96 > sqrtPriceLimitX96:
					target = sqrtPriceLimitX96
				else:
					target = stepSqrtPriceNextX96

			print("stateAmountSpecifiedRemaining: ", stateAmountSpecifiedRemaining)
			print("stateSqrtPriceX96: ", stateSqrtPriceX96 )
			print("sqrtPriceLimitX96: ", sqrtPriceLimitX96)
			print("target: ", target)
			print("stateLiquidity: ", stateLiquidity)

			stateSqrtPriceX96, stepAmountIn, stepAmountOut, stepFeeAmount = self.computeSwapStep(stateSqrtPriceX96, target, stateLiquidity, stateAmountSpecifiedRemaining, self.feeTeir, zeroForOne)
			print("State Fee Amount: ", stepFeeAmount)
			print("Step Amount In: ", stepAmountIn)
			print("Step Amount Out: ", stepAmountOut)
			if exactInput:
				stateAmountSpecifiedRemaining = stateAmountSpecifiedRemaining - (stepAmountIn + stepFeeAmount )
				stateAmountCalculated = stateAmountCalculated - stepAmountOut
			else:
				stateAmountSpecifiedRemaining += stepAmountOut
				stateAmountCalculated += (stepAmountIn + stepFeeAmount)

			if stateSqrtPriceX96 == stepSqrtPriceNextX96:
				if stepInitialized:
					liquidityNet = (self.tickDataProvider.getTick(stepTickNext)).liquidityNet
					if zeroForOne:
						liquidityNet = liquidityNet * -1
					stateLiquidity = self.sqrtPriceMath.addDelta(stateLiquidity, liquidityNet)

				stateTick = stepTickNext - 1 if zeroForOne else stepTickNext
			elif stateSqrtPriceX96 != stepSqrtPriceStartX96:
				stateTick = self.sqrtPriceMath.getTickAtSqrtRatio(stateSqrtPriceX96)
			#print("stateAmountSpecifiedRemaining: ", stateAmountSpecifiedRemaining)
			#print("stateSqrtPriceX96: ", stateSqrtPriceX96)
			#print("sqrtPriceLimitX96: ", sqrtPriceLimitX96)
			#print("stateAmountCalculated: ", stateAmountCalculated)

		#print("stateAmountSpecifiedRemaining: ", stateAmountSpecifiedRemaining)
		#print("stateSqrtPriceX96: ", stateSqrtPriceX96)
		#print("sqrtPriceLimitX96: ", sqrtPriceLimitX96)
		#print("stateAmountCalculated: ", stateAmountCalculated)
		return stateAmountCalculated, stateSqrtPriceX96, stateLiquidity, stateTick


			


	def getOutputAmount(self, inputAmount, sqrtPriceLimitX96):
		#print("ERIC")
		zeroForOne = inputAmount.currency.address == self.token0.address
		# print(zeroForOne)
		# print(inputAmount.currency.address)
		# print(self.tok)
		outputAmount, sqrtRatioX96, liquidity, tickCurrent = self.swap(zeroForOne, inputAmount.quotient(), sqrtPriceLimitX96)
		# print("Output Amount: ", outputAmount)
		# print("SQRT RATIO: ", sqrtRatioX96)
		# print("liquidity: ", liquidity)
		# print("Tick Current: ", tickCurrent)

		outputToken = self.token1 if zeroForOne else self.token0
		
		am = CurrencyAmount(outputToken, outputAmount*-1)
		#sys.exit()
		return (am, Pool(self.token0, self.token1, self.feeTeir, sqrtRatioX96, liquidity, tickCurrent, self.tickDataProvider.ticks, self.address, self.tickSpacing ))


	def getInputAmount(self, outputAmount, sqrtPriceLimitX96):
		zeroForOne = inputAmount.currency.address == self.token0.address
		# print(zeroForOne)
		# print(inputAmount.currency.address)
		# print(self.tok)
		inputAmount, sqrtRatioX96, liquidity, tickCurrent = self.swap(zeroForOne, (outputAmount.quotient())*-1, sqrtPriceLimitX96)
		# print("Output Amount: ", outputAmount)
		# print("SQRT RATIO: ", sqrtRatioX96)
		# print("liquidity: ", liquidity)
		# print("Tick Current: ", tickCurrent)

		inputToken = self.token0 if zeroForOne else self.token1
		return (CurrencyAmount(inputToken, inputAmount), Pool(self.token0, self.token1, self.feeTeir, sqrtRatioX96, liquidity, tickCurrent, self.tickDataProvider.ticks, self.address, self.tickSpacing ))

	def priceAtTick(self, tick):
		return (10 ** (self.token1.decimals - self.token0.decimals)) / (1.0001 ** (tick))

	#https://github.com/Uniswap/uniswap-v3-core/blob/234f27b9bc745eee37491802aa37a0202649e344/contracts/UniswapV3Pool.sol
	#def mint(self, tickLower, tickUpper, amount):

	def createTVLDistrubtion(self):
		activeTickProcessed = self.tickDataProvider.getTick(self.tickCurrent) #Index not tickIDX
		print("ACTIVE PRICE: ", activeTickProcessed.price0)

		for index, tick in enumerate(self.tickDataProvider.ticks):
			if index != 0:
				prevTick = self.tickDataProvider.ticks[index - 1]
			tick.setLiquidityActive(prevTick.liquidityActive + tick.liquidityNet)
			#Getting Price information
			active = (tick.tickIdx == activeTickProcessed.tickIdx)
			
			sqrtPriceX96 = self.sqrtPriceMath.getSqrtRatioAtTick(tick.tickIdx)

			feeAmount = self.feeTeir
			mockTicks = [Tick(0, tick.tickIdx - self.tickSpacing, tick.liquidityNet * -1, tick.liquidityGross, self.token0, self.token1), tick]
			tickPool =  Pool(self.token0, self.token1, int(self.feeTeir), sqrtPriceX96, tick.liquidityActive, tick.tickIdx, mockTicks, self.address, self.tickSpacing)
			if index != 0:
				nextSqrtX96 = self.sqrtPriceMath.getSqrtRatioAtTick(self.tickDataProvider.ticks[index - 1].tickIdx)
				maxAmountToken0 = CurrencyAmount(self.token0, constants.MaxUnit128)
				
				outputRes0 = tickPool.getOutputAmount(maxAmountToken0, nextSqrtX96)

				token1Amount = outputRes0[0]
				self.tickDataProvider.ticks[index - 1].setTvl(token1Amount.quotient() / 1000000000000000000, False)
				self.tickDataProvider.ticks[index - 1].setTvl(token1Amount.quotient() / 1000000000000000000 * tick.price0, True)
				

		#Taking into account the first Tick which we can't get a value for?
		self.tickDataProvider.ticks[-1].setTvl(0, False)	
		self.tickDataProvider.ticks[-1].setTvl(0, True)

		x = []
		liq = []
		amountEth = []
		for tick in self.tickDataProvider.ticks:
			amountEth.append(tick.tvlToken1)
			x.append(tick.price0)

		barWidth = self.feeTierToBarWidth(self.feeTeir, activeTickProcessed.price0)
		barlist = plt.bar(x, amountEth, width=barWidth)
		#barlist[numSurroundingTicks].set_color('r')
		#barlist[numSurroundingTicks].set_label(("Current Tick = {} usd".format(round(pool.tickDataProvider.ticks[numSurroundingTicks].price0, 2))))
		plt.xlabel("Price {} / {}".format(self.token0.symbol, self.token1.symbol))
		plt.ylabel("Total Liquidity")
		plt.title("{} / {} liquidity locked".format(self.token0.symbol, self.token1.symbol))
		#plt.legend()
		plt.show()

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

	def quotient(self):
		return self.price.quotient()
	

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







