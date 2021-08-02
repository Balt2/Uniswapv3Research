import testGraph
import swapData
import time
import mintBurnPull
import matplotlib.pyplot as plt
import math

sleepTime = 10
currentTickIdx = 0 
numberOfPrinciples = 9
liquidityVal = [10000.0 * i for i in range(1, 1 + numberOfPrinciples)] #5 etherum tokens
etherumVal = []
etherumValArr = [[] for i in range(0, numberOfPrinciples)]
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
volGraph = [0]
#Represents the number of buckets we will unifromaly distrubute liquilty in.
strategy = 3.0 
#Represents the current bucket we are in relative to where our liquidity is distriubuted. 0 is center of distribution
currentBucket = 0

#60 Price values
historicalPrice = []

def hourVolitility(price):
	historicalPrice.pop(0)
	historicalPrice.append(price)
	numerator = 0 
	for i in range(59):
		numerator += (abs(price - historicalPrice[i]) * (i+1)/60) ** 2
	numerator = math.sqrt(numerator)
	return numerator / price

while counter < 250: #Do every 1 minute

	activeTick, currentPrice = testGraph.getActiveTick()

	blocks, latestBlock = swapData.getBlockArray()
	if blocks == "ERROR" or activeTick == "ERROR":
		print("NO NEW VALUES. ERROR GETTING DATA")
	else:
		if counter % 10 == 0:	
			moveFee = mintBurnPull.getAverageTransactionFee()
			if moveFee == "ERROR":
				continue
			print(moveFee)
			moveFee = moveFee*currentPrice*.8
			print(moveFee)


		if counter == 0:
			currentBlock = latestBlock
			for i in range(len(liquidityVal)):
				etherumVal.append(liquidityVal[i]/currentPrice)
				etherumValArr[i].append(liquidityVal[i])
			result = map(lambda x: x + moveFee, liquidityVal)
			liquidityVal = list(result)
			print(liquidityVal)
			historicalPrice = [currentPrice for i in range(60)]

		#Array containing values if just hold Etheruem 
		for i in range(len(liquidityVal)):
			etherumValArr[i].append(etherumVal[i]*currentPrice)

		#Update hourVolitiity
		vol = hourVolitility(currentPrice)
		print("Volititility: ", vol)
		volGraph.append(vol)

		if activeTick.tickIdx != currentTickIdx:
			if abs(currentBucket) > strategy // 2 or strategy == 1.0 or counter == 0:
				newFee = 2*moveFee
				totalFee += newFee
				feeArr.append(totalFee)
				result = map(lambda x: x - newFee, liquidityVal)
				liquidityVal = list(result)
				print(liquidityVal)
				currentTickIdx = activeTick.tickIdx
				numMoves += 1
				currentBucket = 0
			elif activeTick.tickIdx < currentTickIdx:
				currentBucket += -1
				currentTickIdx = activeTick.tickIdx
			elif activeTick.tickIdx > currentTickIdx:
				currentBucket += 1
				currentTickIdx = activeTick.tickIdx



		newValue = [0 for i in range(0, numberOfPrinciples)]
		blockValue = 0
		for block in blocks:
			if currentBlock < block.blockNumber:
				blockValue += block.totalUSD
				result = map(lambda x, y: x + block.totalUSD * ( (y/strategy) / (activeTick.tvlToken0 + (y/strategy))) * .003, newValue, liquidityVal)
				newValue = list(result)
				currentBlock = block.blockNumber
				totalSwapValue += blockValue
				totalLiquitity += activeTick.tvlToken0

		result = map(lambda x, y: x + y, totalReward, newValue)
		totalReward = list(result)

		result = map(lambda x, y: x + y, liquidityVal, newValue)
		liquidityVal = list(result)

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
		
		#print(liqArr)
		#liqArr.append(liquidityVal)
		counter += 1
		time.sleep(sleepTime)


fig, axs = plt.subplots(3, 3)
for i in range(0, numberOfPrinciples):
	axs[i % 3, i // 3].plot(counterArr, liqArr[i], label = "Liquidity Provided")
	axs[i % 3, i // 3].plot(counterArr, etherumValArr[i], label = "#HODL")
	axs[i % 3, i // 3].set_title('Liquidity Over Time. P = {}. S = {}'.format((i+1)*10000, strategy), fontsize = 8)

plt.xlabel('Time', fontsize = 8)
plt.ylabel('Liquidity', fontsize = 8)
plt.legend()
plt.show()
print(volGraph)
print(counterArr)


