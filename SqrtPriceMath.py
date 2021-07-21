import constants
import math

class SqrtPriceMath:
	def __init__(self, hi=0):
		self.hi = hi

	def multiplyIn256(self, x, y):
		product = x * y
		#TODO HOW SHOULD I CORRECTLY CAST THIS AS INT?
		return (int(product) & constants.MaxUint256) 

	def addIn256(self, x, y):
		summ = x + y
		return (summ & constants.MaxUint256)

	def mulDivRoundingUp(self,a, b, denominator):
		product = a * b
		result = product / denominator

		if product % denominator != 0:
			result += 1

		return result

	def getAmount0Delta(self, sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
		if sqrtRatioAX96 > sqrtRatioBX96:
			sqrtRatioAX96, sqrtRatioBX96 = sqrtRatioBX96, sqrtRatioAX96

		numerator1 = liquidity << 96
		numerator2 = sqrtRatioBX96 - sqrtRatioAX96

		if roundUp:
			return self.mulDivRoundingUp(self.mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96), 1, sqrtRatioAX96) 
		else:
			return ((numerator2 * numerator1) / sqrtRatioBX96) / sqrtRatioAX96

	def getAmount1Delta(self, sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
		if sqrtRatioAX96 > sqrtRatioBX96:
			sqrtRatioAX96, sqrtRatioBX96 = sqrtRatioBX96, sqrtRatioAX96

		if roundUp:
			return self.mulDivRoundingUp(liquidity, (sqrtRatioBX96 - sqrtRatioAX96), constants.Q96)
		else:
			return (liquidity * (sqrtRatioBX96 - sqrtRatioAX96)) / constants.Q96

	def getNextSqrtPriceFromInput(self, sqrtPX96, liquidity, amountIn, zeroForOne):
		if zeroForOne:
			return self.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, True)
		else:
			return self.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountIn, True)


	def getNextSqrtPriceFromOutput(self, sqrtPX96, liquidity, amountOut, zeroForOne):
		if zeroForOne:
			return self.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountOut, False)
		else:
			return self.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountOut, False)


	def getNextSqrtPriceFromAmount0RoundingUp(self, sqrtPX96, liquidity, amount, add):
		if amount == 0:
			return sqrtPX96

		numerator1 = liquidity << 96

		if add:
			product = self.multiplyIn256(amount, sqrtPX96)
			if product / amount == sqrtPX96:
				denominator = self.addIn256(numerator1, product)
				if denominator >= numerator1:
					return self.mulDivRoundingUp(numerator1, sqrtPX96, denominator)
			return self.mulDivRoundingUp(numerator1, 1, (numerator1 / sqrtPX96) + amount)
		else:
			product = self.multiplyIn256(amount, sqrtPX96)

			denominator = numerator1 - product

			return self.mulDivRoundingUp(numerator1, sqrtPX96, denominator)

	def getNextSqrtPriceFromAmount1RoundingDown(self, sqrtPX96, liquidity, amount, add):
		if add:
			quotient = (amount << 96) / liquidity if amount <= constants.MaxUint160 else (amount * constants.Q96) / liquidity
			return sqrtPX96 + quotient
		else:
			quotient = self.mulDivRoundingUp(amount, constants.Q96, liquidity)
			return sqrtPX96 - quotient

	def mostSignificantBiit(self, x):
		powersOf2 = [(128, 2 ** 128), (64, 2 ** 64), (32, 2 ** 32), (16, 2 ** 16), (8, 2 ** 8), (4, 2 ** 4), (2, 2 ** 2), (1, 2 ** 1)]
		msb = 0
		for index, val in enumerate(powersOf2):
			if x >= val[1]:
				x = x >> val[0]
				msb += val[0]

		return msb


	def sqrtRatioAtTick(self, tick):
		absTick = abs(tick)
		return (math.sqrt(1.0001)) ** absTick


	def getTickAtSqrtRatio(self, sqrtRatioX96):
		#TODO HOW SHOULD I CORRECTLY CAST THIS AS INT?
		sqrtRatioX128 = int(sqrtRatioX96) << 32
		msb = self.mostSignificantBiit(sqrtRatioX128)
		r = 0
		if msb >= 128:
			r = sqrtRatioX128 >> msb  - 127
		else:
			r = sqrtRatioX128 << 127 - msb

		log2 = (msb - 128) << 64

		for i in range(14):
			r = (r*r) >> 127
			f = r >> 128
			log2 = log2 | (f << 63 - i)
			r = r >> f

		logSqrt1001 = log2 * 255738958999603826347141

		tickLow = (logSqrt1001 - 3402992956809132418596140100660247210) >> 128

		tickHigh = (logSqrt1001 + 291339464771989622907027621153398088495) >> 128

		if tickLow == tickHigh:
			return tickLow
		elif self.sqrtRatioAtTick(tickHigh) <= sqrtRatioX96:
			return tickHigh
		else:
			return tickLow

	def addDelta(self, x, y):
		if y < 0:
			return x - (y * -1)
		else:
			return x + y

