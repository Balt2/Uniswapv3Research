import math
import constants


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
	def __init__(self, token0, token1, feeTeir, sqrtRatio ,liquidity, tick, mockTicks, address):
		self.address = address
		self.feeTeir = feeTeir
		self.token0 = token0
		self.token1 = token1
		self.liquidity = liquidity
		self.sqrtRatio = sqrtRatio
		self.tick = tick
		self.mockTicks = mockTicks
		self.tickCurrentSqrtRatioX96 = self.sqrtRatioAtTick(tick)
		self.nextTickSqrtRatioX96 = self.sqrtRatioAtTick(tick + 1)


	def sqrtRatioAtTick(self, tick):
		absTick = abs(tick)
		return (sqrt(1.0001)) ** absTick

	def getToken0Price(self):
		return Price(self.token0, self.token1, constants.q192, self.sqrtRatio * self.sqrtRatio)

	def getToken1Price(self):
		return Price(self.token1, self.token0, self.sqrtRatio * self.sqrtRatio, constants.q192)

	def priceOf(self, token):
		if token.address == self.token0.address:
			return self.token0
		else:
			return self.token1
		#TODO Check if token is not token0 or token1

	def getOutputAmount(self, inputAmount, sqrtPriceLimit, token0ForToken1):
		self.swap(token0ForToken1, inputAmount.quotient(), sqrtPriceLimit)

	#def swap(self, token0ForToken1, amountSpecified, sqrtPriceLimit):

		

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
	def __init__(self, token, numerator, denominator):
		self.currency = token
		self.deciimalScale = 10 ** token.decimals
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







