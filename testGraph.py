from python_graphql_client import GraphqlClient
from Tick import *
import matplotlib.pyplot as plt
from SqrtPriceMath import *
from TickList import *
import constants
#import sys


client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")

numSurroundingTicks = 10

#https://github.com/Uniswap/uniswap-v3-sdk/blob/aeb1b09/src/utils/tickMath.ts#L26
minTick = -887272
maxTick = 887272

usdcUSDT = "0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf"
usdcETH = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
wbtcETH = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
usdtETH = "0x4e68ccd3e89f51c3074ca5072bbac773960dfa36"
daiUSDC = "0x6c6bc977e13df9b0de53b251522280bb72383700"
mmUSDC = "0x84383fb05f610222430f69727aa638f8fdbf5cc1"
shibETH = "0x5764a6f2212d502bc5970f9f129ffcd61e5d7563"
#poolAddress = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
#poolAddress = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
#poolAddress = "0x6c6bc977e13df9b0de53b251522280bb72383700"
poolAddress = usdcETH

if poolAddress == wbtcETH or poolAddress == usdcETH:
	divisionFactor = 1000000000000000000
elif poolAddress == usdtETH:
	divisionFactor = 1000000



def computeSurroundingTicks(activeTickP, tickSpacing, numSurroundingTicks, asc, tickDict, token0, token1):
	previousTickProcessed = activeTickP
	processedTicks = []
	for i in range(numSurroundingTicks):
		currentTickIdx = 0
		if asc:
			currentTickIdx = previousTickProcessed.tickIdx + tickSpacing
		else:
			currentTickIdx = previousTickProcessed.tickIdx - tickSpacing

		if currentTickIdx < minTick or currentTickIdx > maxTick:
			break

		currentTickProcessed = Tick(previousTickProcessed.liquidityActive, currentTickIdx, 0, 0, token0, token1)

		if currentTickIdx in tickDict:
			liquidityNet = int((tickDict[currentTickIdx])['liquidityNet'])
			liquidityGross = int((tickDict[currentTickIdx])['liquidityGross'])
			currentTickProcessed.setLiquidityNet(liquidityNet)
			currentTickProcessed.setLiquidityGross(liquidityGross)

		if asc:
			currentTickProcessed.setLiquidityActive(previousTickProcessed.liquidityActive + currentTickProcessed.liquidityNet)
		else:
			currentTickProcessed.setLiquidityActive(previousTickProcessed.liquidityActive - previousTickProcessed.liquidityNet)

		#print(currentTickProcessed.liquidityActive , ", ", currentTickProcessed.price0)
		processedTicks.append(currentTickProcessed)
		previousTickProcessed = currentTickProcessed

	if not asc:
		processedTicks.reverse()

	return processedTicks

def tickDataToDict(data):
	tickDict = {} 
	for tick in data:
		index = int(tick['tickIdx'])
		tickDict[index] = tick
	return tickDict

def feeTierToSpacing(feeTier):
	if feeTier == "10000":
		return 200
	elif feeTier == "3000":
		return  60
	elif  feeTier == "500":
		return 10
	else:
		print("ERROR")

def feeTierToBarWidth(feeTier, currentPrice):
	feeTierInt = int(feeTier)
	width = abs(currentPrice - currentPrice*(1 + feeTierInt*.000001) )
	return width

def createPoolWithTicks():
	poolQuery = """
		query pool($poolAddress: String!) {
		    pool(id: $poolAddress) {
		      tick
		      token0 {
		        symbol
		        id
		        decimals
		      }
		      token1 {
		        symbol
		        id
		        decimals
		      }
		      feeTier
		      sqrtPrice
		      liquidity
		      totalValueLockedToken0
	          totalValueLockedToken1
	          totalValueLockedUSD
		    }
	  }
	"""

	souroundingTicks = """
		query souroundingTicks($poolAddress: String, $tickIdxUpperBound: Int, $tickIdxLowerBound: Int, $skip: Int){
			ticks(
				first: 1000
				skip: $skip
				where: {poolAddress: $poolAddress, tickIdx_lte: $tickIdxUpperBound, tickIdx_gte: $tickIdxLowerBound}
			){
				tickIdx
				liquidityGross
				liquidityNet
				price0
				price1
				volumeToken0
				volumeToken1
				volumeUSD
				untrackedVolumeUSD
				liquidityProviderCount
				feesUSD
				feeGrowthOutside1X128
			}
		}

	"""


	#Pull Pool Data
	try:
		poolDataQuery = client.execute(query=poolQuery, variables={"poolAddress": poolAddress} )
	except: 
		return "ERROR", "ERROR IN TEST GRAPH, Pool Query", "ERROR"

	if 'data' not in poolDataQuery.keys():
		return "ERROR", "Unkown Error", "ERROR"
	#print(poolDataQuery)
	poolCurrentTick = int(((poolDataQuery['data'])['pool'])['tick'])
	poolFeeTier = ((poolDataQuery['data'])['pool'])['feeTier']
	tickSpacing = feeTierToSpacing(poolFeeTier)

	#Calculating Tick information
	activeTickIdx = (poolCurrentTick // tickSpacing) *  tickSpacing

	tickIdxLowerBound = activeTickIdx - numSurroundingTicks * tickSpacing
	tickIdxUpperBound = activeTickIdx + numSurroundingTicks * tickSpacing


	try:
		ticksResult = client.execute(query=souroundingTicks, variables={"poolAddress": poolAddress, "skip": 1, "tickIdxUpperBound": tickIdxUpperBound, "tickIdxLowerBound": tickIdxLowerBound })
	except:
		return "ERROR", "ERROR IN TEST GRAPH, Tick Result", "ERROR"

	if 'data' not in ticksResult.keys():
		return "ERROR", "Unkown Error", "ERROR"
	#print(ticksResult)
	tickDict = tickDataToDict((ticksResult['data'])['ticks'])

	token0 = Token(poolDataQuery['data']['pool']['token0']['id'], poolDataQuery['data']['pool']['token0']['symbol'], int(poolDataQuery['data']['pool']['token0']['decimals']) )

	token1 = Token(poolDataQuery['data']['pool']['token1']['id'], poolDataQuery['data']['pool']['token1']['symbol'], int(poolDataQuery['data']['pool']['token1']['decimals']) )

	if activeTickIdx < minTick:
		activeTickIdx = minTick

	if  activeTickIdx > maxTick:
		activeTickIdx = maxTick


	#Active Tick Processed
	liquidityActive = int(((poolDataQuery['data'])['pool'])['liquidity'])

	activeTickProcessed = Tick(liquidityActive, activeTickIdx, 0,0, token0, token1)

	if activeTickIdx in tickDict:
		liquidityNet = int((tickDict[activeTickIdx])['liquidityNet'])
		liquidityGross = int((tickDict[activeTickIdx])['liquidityGross'])
		activeTickProcessed.setLiquidityNet(liquidityNet)
		activeTickProcessed.setLiquidityGross(liquidityGross)
	# print("PRICE 0: ", activeTickProcessed.price0)
	# print("Active Tick IDX ", activeTickProcessed.tickIdx)
	# print("PRICE 1: ", activeTickProcessed.price1)


	subsequentTicks = computeSurroundingTicks(activeTickProcessed, tickSpacing, numSurroundingTicks, True, tickDict, token0, token1)
	#print(activeTickProcessed.liquidityActive, ", ", activeTickProcessed.price0)
	previousTicks = computeSurroundingTicks(activeTickProcessed, tickSpacing, numSurroundingTicks, False, tickDict, token0, token1)
	previousTicks.append(activeTickProcessed)
	allTicks = previousTicks + subsequentTicks


	wholePool = Pool(token0, token1, int(poolFeeTier), int(((poolDataQuery['data'])['pool'])['sqrtPrice']), liquidityActive, activeTickProcessed.tickIdx, allTicks,poolAddress, tickSpacing )
	currentPriceAtCurrentTick = wholePool.priceAtTick(poolCurrentTick)




	sqrtPriceMath = SqrtPriceMath()


	#Computing Amount of token 0/1 for each tick. Based on https://github.com/Uniswap/uniswap-v3-info/blob/836a38d236595e0ac18ae470102556f55b1da788/src/components/DensityChart/index.tsx#L157
	for index, tick in enumerate(wholePool.tickDataProvider.ticks):

		#Getting Price information
		active = (tick.tickIdx == activeTickProcessed.tickIdx)

		sqrtPriceX96 = sqrtPriceMath.getSqrtRatioAtTick(tick.tickIdx)

		feeAmount = wholePool.feeTeir
		mockTicks = [Tick(0, tick.tickIdx - wholePool.tickSpacing, tick.liquidityNet * -1, tick.liquidityGross, token0, token1), tick]
		tickPool =  Pool(token0, token1, int(poolFeeTier), sqrtPriceX96, tick.liquidityActive, tick.tickIdx, mockTicks, poolAddress, tickSpacing)
		if index != 0:
			nextSqrtX96 = sqrtPriceMath.getSqrtRatioAtTick(wholePool.tickDataProvider.ticks[index - 1].tickIdx)
			maxAmountToken0 = CurrencyAmount(token0, constants.MaxUnit128)
			
			outputRes0 = tickPool.getOutputAmount(maxAmountToken0, nextSqrtX96)

			token1Amount = outputRes0[0]
			wholePool.tickDataProvider.ticks[index - 1].setTvl(token1Amount.quotient() / divisionFactor, False)
			wholePool.tickDataProvider.ticks[index - 1].setTvl(token1Amount.quotient() / divisionFactor * tick.price0, True)
			

	#Taking into account the first Tick which we can't get a value for?
	wholePool.tickDataProvider.ticks[-1].setTvl(0, False)	
	wholePool.tickDataProvider.ticks[-1].setTvl(0, True)
	return wholePool, poolFeeTier, currentPriceAtCurrentTick

def getActiveTick():
	pool, poolFeeTeir, currentPrice = createPoolWithTicks()
	if pool == "ERROR":
		return "ERROR", "ERROR"
	else:
		return pool.tickDataProvider.ticks[numSurroundingTicks], currentPrice



#For Graph
pool, poolFeeTier, curPrice = createPoolWithTicks()

x = []
liq = []
amountEth = []
for tick in pool.tickDataProvider.ticks:
	amountEth.append(tick.tvlToken1)
	x.append(tick.price0)
	liq.append(tick.liquidityActive)
	print("Price 0: ", tick.price0)
	print("Price 1: ", tick.price1)

	print("TVL Token 1: ", tick.tvlToken1)
	print("TVL Token 0: ", tick.tvlToken0)
#Building Graph

barWidth = feeTierToBarWidth(poolFeeTier, pool.tickDataProvider.ticks[numSurroundingTicks].price0)
barlist = plt.bar(x, amountEth, width=barWidth)
barlist[numSurroundingTicks].set_color('r')
barlist[numSurroundingTicks].set_label(("Current Tick = {} usd".format(round(pool.tickDataProvider.ticks[numSurroundingTicks].price0, 2))))
plt.xlabel("Price {} / {}".format(pool.token0.symbol, pool.token1.symbol))
plt.ylabel("Total Liquidity")
plt.title("{} / {} liquidity locked".format(pool.token0.symbol, pool.token1.symbol))
plt.legend()
plt.show()





