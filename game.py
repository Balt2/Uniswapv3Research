import testGraph
import swapData
import time
import mintBurnPull
import matplotlib.pyplot as plt

sleepTime = 60
currentTickIdx = 0 
liquidityVal = 10000.0 #5 etherum tokens
moveFee = 18
liquidityVal = liquidityVal + moveFee
currentBlock = 12884968	
counter = 0
numMoves = -1
timeArr = []
liqArr = []
while counter < 500: #Do every 1 minute

	activeTick = testGraph.getActiveTick()
	blocks = swapData.getBlockArray()

	if counter % 10 == 0:
		moveFee = mintBurnPull.getAverageTransactionFee()
		print(moveFee)
		moveFee = moveFee*activeTick.price0
		print(moveFee)

	if activeTick.tickIdx != currentTickIdx:
		liquidityVal = liquidityVal - 2*moveFee
		currentTickIdx = activeTick.tickIdx
		numMoves += 1

	newValue = 0
	blockValue = 0
	for block in blocks:
		if currentBlock < block.blockNumber:
			blockValue += block.totalUSD
			newValue += block.totalUSD * (liquidityVal / activeTick.tvlToken0) * .003
			currentBlock = block.blockNumber

	liquidityVal = newValue + liquidityVal
	print("TIME IN SECONDS: ", counter * sleepTime)
	print("Current Liquidity Value: ", liquidityVal)
	print("Current Eth Price: ", activeTick.price0)	
	print("New Value: ", newValue)	
	print("Price Moves: ", numMoves)
	print("Block Value: ", blockValue )
	timeArr.append(counter)
	liqArr.append(liquidityVal)
	counter += 1
	time.sleep(sleepTime)

plt.plot(timeArr, liqArr)
plt.show()

# print(activeTick)
# print(activeTick.tickIdx)
# print(activeTick.price0)
# print(activeTick.tvlToken1)