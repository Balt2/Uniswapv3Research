import testGraph
import swapData
import time
import mintBurnPull
import matplotlib.pyplot as plt

sleepTime = 60
currentTickIdx = 0 
numberOfPrinciples = 9
liquidityVal = [5 * i for i in range(1, 1 + numberOfPrinciples)] #5 etherum tokens
moveFee = 18
currentBlock = 12884968	
counter = 0
numMoves = -1
counterArr = [0]
liqArr = [[liquidityVal[i]] for i in range(0, numberOfPrinciples)]
feeArr = []
totalFee = 0
totalReward = [0 for i in range(0, numberOfPrinciples)]
totalSwapValue = 0
totalLiquitity = 0

while counter < 250: #Do every 1 minute

	activeTick = testGraph.getActiveTick()

	blocks, latestBlock = swapData.getBlockArray()
	if blocks == "ERROR" or activeTick == "ERROR":
		print("NO NEW VALUES. ERROR GETTING DATA")
	else:
		if counter % 10 == 0:	
			moveFee = mintBurnPull.getAverageTransactionFee()
			print(moveFee)
			moveFee = moveFee*.8
			print(moveFee)


		if counter == 0:
			currentBlock = latestBlock
			result = map(lambda x: x + moveFee, liquidityVal)
			liquidityVal = list(result)
			print(liquidityVal)

		

		if activeTick.tickIdx != currentTickIdx:
			newFee = 2*moveFee
			totalFee += newFee
			feeArr.append(totalFee)
			result = map(lambda x: x - newFee, liquidityVal)
			liquidityVal = list(result)
			print(liquidityVal)
			currentTickIdx = activeTick.tickIdx
			numMoves += 1


		newValue = [0 for i in range(0, numberOfPrinciples)]
		blockValue = 0
		for block in blocks:
			if currentBlock < block.blockNumber:
				blockValue += (block.totalUSD / activeTick.price0)
				result = map(lambda x, y: x + (block.totalUSD / activeTick.price0) * (y / (activeTick.tvlToken1 + y)) * .003, newValue, liquidityVal)
				#newValue += block.totalUSD * (liquidityVal / activeTick.tvlToken0) * .003
				newValue = list(result)
				currentBlock = block.blockNumber
				totalSwapValue += blockValue
				totalLiquitity += activeTick.tvlToken1

		result = map(lambda x, y: x + y, totalReward, newValue)
		totalReward = list(result)
		#totalReward += newValue

		result = map(lambda x, y: x + y, liquidityVal, newValue)
		liquidityVal = list(result)
		#liquidityVal += newValue

		print("TIME IN SECONDS: ", counter * sleepTime)
		print("Current Liquidity Value: ", liquidityVal)
		print("Current Eth Price: ", activeTick.price0)	
		print("New Value: ", newValue)	
		print("Price Moves: ", numMoves)
		print("Block Value: ", blockValue )
		print("total fee: ", totalFee)
		print("total reward: ", totalReward)
		print("Total Swap Value: ", totalSwapValue)
		print("Total Liquidity Locked Each: ", totalLiquitity)
		counterArr.append(counter + 1)

		for i in range(0, numberOfPrinciples):
			liqToAdd = liquidityVal[i]
			liqArr[i].append(liqToAdd)
		
		print(liqArr)
		#liqArr.append(liquidityVal)
		counter += 1
		time.sleep(sleepTime)


fig, axs = plt.subplots(3, 3)
for i in range(0, numberOfPrinciples):
	axs[i % 3, i // 3].plot(counterArr, liqArr[i])
	axs[i % 3, i // 3].set_title('Liquidity Over Time ETH. P = {}'.format((i+1)*10000), fontsize = 8)

# plt.subplots_adjust(left=0.1,
#                     bottom=0.1, 
#                     right=0.9, 
#                     top=0.9, 
#                     wspace=0.4, 
#                     hspace=0.4)

plt.xlabel('Time', fontsize = 8)
plt.ylabel('Liquidity', fontsize = 8)
plt.show()

# print("Principle Amount: ", 80000.0)
# plt.plot(counterArr, liqArr)
# plt.show()
