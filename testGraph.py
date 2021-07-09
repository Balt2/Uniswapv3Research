from python_graphql_client import GraphqlClient
from  Tick import *
import matplotlib.pyplot as plt


client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/yekta/uniswap-v3-with-fees-and-amounts")

numSurroundingTicks = 200

#https://github.com/Uniswap/uniswap-v3-sdk/blob/aeb1b09/src/utils/tickMath.ts#L26
minTick = -887272
maxTick = 887272

poolAddress = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
#poolAddress = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"


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
		}
	}

"""

poolDataQuery = client.execute(query=poolQuery, variables={"poolAddress": poolAddress} )
poolCurrentTick = int(((poolDataQuery['data'])['pool'])['tick'])
poolFeeTier = ((poolDataQuery['data'])['pool'])['feeTier']
tickSpacing = feeTierToSpacing(poolFeeTier)
activeTickIdx = (poolCurrentTick // tickSpacing) *  tickSpacing

tickIdxLowerBound = activeTickIdx - numSurroundingTicks * tickSpacing
tickIdxUpperBound = activeTickIdx + numSurroundingTicks * tickSpacing



ticksResult = client.execute(query=souroundingTicks, variables={"poolAddress": poolAddress, "skip": 100, "tickIdxUpperBound": tickIdxUpperBound, "tickIdxLowerBound": tickIdxLowerBound })
tickDict = tickDataToDict((ticksResult['data'])['ticks'])

print(poolDataQuery)

token0 = Token(poolDataQuery['data']['pool']['token0']['id'], poolDataQuery['data']['pool']['token0']['symbol'], int(poolDataQuery['data']['pool']['token0']['decimals']) )

token1 = Token(poolDataQuery['data']['pool']['token1']['id'], poolDataQuery['data']['pool']['token1']['symbol'], int(poolDataQuery['data']['pool']['token1']['decimals']) )

activeTickIdxForPrice = activeTickIdx
if activeTickIdxForPrice < minTick:
	activeTickIdxForPrice = minTick

if  activeTickIdxForPrice > maxTick:
	activeTickIdxForPrice = maxTick


#Active Tick Processed
liquidityActive = int(((poolDataQuery['data'])['pool'])['liquidity'])

activeTickProcessed = Tick(liquidityActive, activeTickIdx, 0,0, token0, token1)

if activeTickIdx in tickDict:
	liquidityNet = int((tickDict[activeTickIdx])['liquidityNet'])
	liquidityGross = int((tickDict[activeTickIdx])['liquidityGross'])
	activeTickProcessed.setLiquidityNet(liquidityNet)
	activeTickProcessed.setLiquidityGross(liquidityGross)
print(activeTickProcessed.price0)
print(activeTickProcessed.tickIdx)
print(activeTickProcessed.price1)

# print(tickDict)
# print(liquidityNet)
# print(liquidityGross)
# print(liquidityActive)
# print(activeTickIdx)
# print(poolDataQuery)

subsequentTicks = computeSurroundingTicks(activeTickProcessed, tickSpacing, numSurroundingTicks, True, tickDict, token0, token1)
previousTicks = computeSurroundingTicks(activeTickProcessed, tickSpacing, numSurroundingTicks, False, tickDict, token0, token1)
previousTicks.append(activeTickProcessed)
allTicks = previousTicks + subsequentTicks

x = []
liq = []
for tick in allTicks:
	x.append(tick.price0)
	liq.append(tick.liquidityActive)


plt.bar(x, liq, width=7)
plt.xlabel("Price {} / {}".format(token0.symbol, token1.symbol))
plt.ylabel("Total Liquidity")
plt.title("{} / {} liquidity locked".format(token0.symbol, token1.symbol))
plt.axvline(activeTickProcessed.price0, color='r', label=("Current Tick = {} usd".format(round(activeTickProcessed.price0, 2))))
plt.legend()
plt.show()
#print(subsequentTicks)

#activeTick  = tickDict[activeTickIdx]

# if True:

# 	print(liquidityActive)










#print(poolDataQuery)