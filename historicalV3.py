from python_graphql_client import GraphqlClient
from Tick import *
import matplotlib.pyplot as plt
from SqrtPriceMath import *
from TickList import *
import constants
import mintBurnPull
import time
import testGraph

client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
wholePool, poolFeeTier, y = testGraph.createPoolWithTicks()
tickDict = {}
for i in range(195060, 202560, 60):
	newTick = Tick(0, i, 0, 0, wholePool.token0, wholePool.token1)
	tickDict[i] = newTick


firstTimestamp = 1620169800
nextTimestamp = firstTimestamp + 30000
burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
while firstTimestamp < time.time():
	print(firstTimestamp - time.time())
	mintResults = mintBurnPull.getMints("asc", 300, firstTimestamp, nextTimestamp)
	mints = mintResults['data']['pool']['mints']
	for mint in mints:
		tickUpper = int(mint['tickUpper'])
		tickLower = int(mint['tickLower'])
		numTicksCovered = (tickUpper - tickLower)/60
		amountMint = float(mint['amount']) / numTicksCovered
		amount0Mint = float(mint['amount0']) / numTicksCovered
		amount1Mint = float(mint['amount1']) / numTicksCovered
		amountUSDMint = float(mint['amountUSD']) / numTicksCovered
		for i in range(tickUpper, tickLower + 1, -60):
			if i in tickDict.keys():
				tickDict[i].updateAmount(amountMint)
				tickDict[i].updateAmount0(amount0Mint)
				tickDict[i].updateAmount1(amount1Mint)
				tickDict[i].updateAmountUSD(amountUSDMint)

	burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
	burns = burnResults['data']['pool']['burns']
	for burn in burns:
		tickUpper = int(burn['tickUpper'])
		tickLower = int(burn['tickLower'])
		numTicksCovered = (tickUpper - tickLower)/60
		amountBurn = float(burn['amount']) / numTicksCovered
		amount0Burn = float(burn['amount0']) / numTicksCovered
		amount1Burn = float(burn['amount1']) / numTicksCovered
		amountUSDBurn = float(burn['amountUSD']) / numTicksCovered
		for i in range(tickUpper, tickLower + 1, -60):
			if i in tickDict.keys():
				tickDict[i].updateAmount(amountBurn*-1)
				tickDict[i].updateAmount0(amount0Burn*-1)
				tickDict[i].updateAmount1(amount1Burn*-1)
				tickDict[i].updateAmountUSD(amountUSDBurn*-1)

	firstTimestamp = nextTimestamp
	nextTimestamp += 30000


keys = list(tickDict.keys())
keys.sort()
x = []
liq = []
for key in keys:
	x.append(tickDict[key].price0)
	liq.append(tickDict[key].amount1)

barWidth = testGraph.feeTierToBarWidth(poolFeeTier, 2500)
plt.bar(x, liq, width=barWidth)
plt.show()


#print(mintResults)