import math

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
		print(self.averageGas)

