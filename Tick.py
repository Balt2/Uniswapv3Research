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
