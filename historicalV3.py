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
import copy
import time
import datetime
import sys


client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
wholePool, poolFeeTier, y = testGraph.createPoolWithTicks()
tickDict = {}
for i in range(195060, 202560, 60):
	newTick = Tick(0, i, 0, 0, wholePool.token0, wholePool.token1)
	tickDict[i] = newTick


# burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
mintDF = createHistoricalData.getMintDataFrame(False)
burnDF = createHistoricalData.getBurnDataFrame(False)
swapDF = createHistoricalData.getSwapDataFrame(False)


def updateTick(tick, pool, liquidityDelta, upper):
	tickToUpdate = wholePool.tickDataProvider.getTick(tick)
	liquidityGrossAfter = wholePool.sqrtPriceMath.addDelta(tickToUpdate.liquidityGross, liquidityDelta)
	tickToUpdate.setLiquidityGross(liquidityGrossAfter)
	if upper:
		newLiquidityNet = tickToUpdate.liquidityNet - liquidityDelta
	else:
		newLiquidityNet = tickToUpdate.liquidityNet + liquidityDelta

	tickToUpdate.setLiquidityNet(newLiquidityNet)

def buildPoolFromScratch():
	newPool = copy.deepcopy(wholePool)
	wholePool.reset()
	ticks = []
	for i in range(195060, 202860, 60):
		newTick = Tick(0, i, 0, 0, wholePool.token0, wholePool.token1)
		ticks.append(newTick)
	tickList = TickList(ticks, 60)
	wholePool.setTickList(tickList)


	allDF = mintDF.append(burnDF, ignore_index=True)
	allDF = allDF.append(swapDF, ignore_index=True)
	allDF = allDF.sort_values(by=['timestamp', 'type'])
	allDF.reset_index(drop=True, inplace=True)
	allDF.to_excel("all.xlsx")
	#Converts tick to one that is initialized
	wholePool.setTickCurrent(swapDF.iloc[0]['tick'])
	wholePool.setSqrtRatioX96(swapDF.iloc[0]['sqrtPriceX96'])
	for index, event in allDF.iterrows():
		print("INDEX IS: ", index)
		print(event['type'])
		if event['type'] == "bMint":
			#https://github.com/Uniswap/uniswap-v3-core/blob/234f27b9bc745eee37491802aa37a0202649e344/contracts/UniswapV3Pool.sol
			liquidityDelta = event['amount']
			#Lower
			tickLower = event['tickLower']
			updateTick(tickLower, wholePool, liquidityDelta, False )
			#Upper
			tickUpper = event['tickUpper']
			updateTick(tickUpper, wholePool, liquidityDelta, True)
			wholePool.addLiquidity(liquidityDelta)
			if wholePool.liquidity < 0:
				print("Pool Liquiid: ", wholePool.liquidity)
				sys.exit()
		elif event['type'] == "cBurn":
			liquidityDelta = event['amount']*-1
  			#Lower
			tickLower = event['tickLower']
			updateTick(tickLower, wholePool, liquidityDelta, False )
			#Upper
			tickUpper = event['tickUpper']
			updateTick(tickUpper, wholePool, liquidityDelta, True)
			wholePool.addLiquidity(liquidityDelta)
			if wholePool.liquidity < 0:
				print("Pool Liquiid: ", wholePool.liquidity)
				sys.exit()
		elif event['type'] == "aSwap":
			if event['amount0'] > event['amount1']:
				zeroForOne = True
				amountSpecified = event['amount0']
			else:
				zeroForOne = False
				amountSpecified = event['amount1']
			if amountSpecified < 0:
				print("Amount Specified: ", amountSpecified)
				sys.exit()
			sqrtPricelim = event['sqrtPriceX96']
			amountCalc, sqrtPriceNext, liquidity, tick = wholePool.swap(zeroForOne, amountSpecified, sqrtPricelim)
			wholePool.setSqrtRatioX96(sqrtPriceNext)
			wholePool.setTickCurrent(tick)
			#wholePool.setLiquidity(liquidity)
	for tick in wholePool.tickDataProvider.ticks:
		print("Tick Index: ", tick.tickIdx)
		print("Tick Net: ", tick.liquidityNet)
		print("Tick Gross: ", tick.liquidityGross)
		print("Tick Active: ", tick.liquidityActive)
		print("Tick Price: ", tick.price0)
		print(datetime.datetime.fromtimestamp(event['timestamp']).strftime('%c'))
	wholePool.createTVLDistrubtion()
		
			
			

def createLiquidityDistribution():
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

#createLiquidityDistribution()
buildPoolFromScratch()

#print(mintResults)