from python_graphql_client import GraphqlClient
from Tick import *
import matplotlib.pyplot as plt
from SqrtPriceMath import *
from TickList import *
import constants
import mintBurnPull
import time
import testGraph
import pandas as pd
import createHistoricalData

client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
wholePool, poolFeeTier, y = testGraph.createPoolWithTicks()
tickDict = {}
for i in range(195060, 202560, 60):
	newTick = Tick(0, i, 0, 0, wholePool.token0, wholePool.token1)
	tickDict[i] = newTick

# burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
mintDF = createHistoricalData.getMintDataFrame()
for index, mint in mintDF.iterrows():
	tickUpper = mint['tickUpper']
	tickLower = mint['tickLower']
	numTicksCovered = 1 #(tickUpper - tickLower)/60
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

burnDF = createHistoricalData.getBurnDataFrame()
for index, burn in burnDF.iterrows():
	tickUpper = burn['tickUpper']
	tickLower = burn['tickLower']
	numTicksCovered = 1 #(tickUpper - tickLower)/60
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



totalUSD = 0
keys = list(tickDict.keys())
keys.sort()
x = []
liq = []
for key in keys:
	totalUSD += tickDict[key].amount0
	x.append(tickDict[key].price0)
	liq.append(tickDict[key].amount)

print(totalUSD)
barWidth = testGraph.feeTierToBarWidth(poolFeeTier, 2500)
plt.bar(x, liq, width=barWidth)
plt.show()


#print(mintResults)