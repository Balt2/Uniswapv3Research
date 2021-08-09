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
import swapData

client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
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

def getMintDataFrame():
	mintsDataFrame = pd.read_pickle("mints.pkl")
	# print(mintsDataFrame.iloc[-1])

	rowList = []
	firstTimestamp = int(mintsDataFrame.iloc[-1]['timestamp']) #1620169800 #int(mintsDataFrame.iloc[-1]['timestamp'])  #
	nextTimestamp = firstTimestamp + 30000
	while firstTimestamp < time.time():
		print(firstTimestamp - time.time())
		mintResults = mintBurnPull.getMints("asc", 300, firstTimestamp, nextTimestamp)
		if mintResults != "ERROR":
			mints = mintResults['data']['pool']['mints']
			for mint in mints:
				newMint = mint
				newMint['amount'] = float(mint['amount'])
				newMint['amount0'] = float(mint['amount0'])
				newMint['amount1'] = float(mint['amount1'])
				newMint['amountUSD'] = float(mint['amountUSD'])
				newMint['tickLower'] = int(mint['tickLower'])
				newMint['tickUpper'] = int(mint['tickUpper'])
				newMint['timestamp'] = int(mint['timestamp'])
				newMint['blockNumber'] = int(newMint['transaction']['blockNumber'])
				newMint['gasPrice'] = int(newMint['transaction']['gasPrice'])
				newMint['gasUsed'] = int(newMint['transaction']['gasUsed'])
				newMint.pop('transaction')
				rowList.append(newMint)
		firstTimestamp = nextTimestamp
		nextTimestamp += 30000

	#mintsDataFrame = pd.DataFrame(rowList)
	mintsDataFrame = mintsDataFrame.append(rowList, ignore_index=True, sort=False)
	mintsDataFrame.to_excel("mints.xlsx")
	mintsDataFrame.to_pickle("mints.pkl")
	# print(mintsDataFrame.iloc[-1])
	return mintsDataFrame

def getBurnDataFrame():
	burnsDataFrame = pd.read_pickle("burns.pkl")
	# print(burnsDataFrame.iloc[-1])
	rowList = []
	firstTimestamp = int(burnsDataFrame.iloc[-1]['timestamp']) #1620169800  #int(burnsDataFrame.iloc[-1]['timestamp'])  #
	nextTimestamp = firstTimestamp + 30000
	while firstTimestamp < time.time():
		print(firstTimestamp - time.time())
		burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
		if burnResults != "ERROR":
			burns = burnResults['data']['pool']['burns']
			for burn in burns:
				newBurn = burn
				newBurn['amount'] = float(burn['amount'])
				newBurn['amount0'] = float(burn['amount0'])
				newBurn['amount1'] = float(burn['amount1'])
				newBurn['amountUSD'] = float(burn['amountUSD'])
				newBurn['tickLower'] = int(burn['tickLower'])
				newBurn['tickUpper'] = int(burn['tickUpper'])
				newBurn['timestamp'] = int(burn['timestamp'])
				newBurn['blockNumber'] = int(newBurn['transaction']['blockNumber'])
				newBurn['gasPrice'] = int(newBurn['transaction']['gasPrice'])
				newBurn['gasUsed'] = int(newBurn['transaction']['gasUsed'])
				newBurn.pop('transaction')
				rowList.append(newBurn)
		firstTimestamp = nextTimestamp
		nextTimestamp += 30000

	#burnsDataFrame = pd.DataFrame(rowList)
	burnsDataFrame = burnsDataFrame.append(rowList, ignore_index=True, sort=False)
	burnsDataFrame.to_excel("burns.xlsx")
	burnsDataFrame.to_pickle("burns.pkl")
	return burnsDataFrame

def getSwapDataFrame():
	swapResults = mintBurnPull.getSwaps("desc", 2)
	
	pool, feeTier, priceAtTick = testGraph.createPoolWithTicks()
	pool.setSqrtRatioX96(int(swapResults['data']['pool']['swaps'][1]['sqrtPriceX96']))
	swapAmount0 = CurrencyAmount(pool.token0, float(swapResults['data']['pool']['swaps'][0]['amount0']))
	swapAmount1 = CurrencyAmount(pool.token1, float(swapResults['data']['pool']['swaps'][0]['amount1']))
	print(swapResults)
	print("BETTINA")
	if swapAmount0.quotient() > swapAmount1.quotient():
		print(int(swapResults['data']['pool']['swaps'][0]['sqrtPriceX96'] ))
		print(swapAmount0.quotient())
		print(swapAmount0.currency.symbol)
		amount, p = pool.getOutputAmount(swapAmount0, int(swapResults['data']['pool']['swaps'][0]['sqrtPriceX96'] ))
		print(amount)
		print("SWAP AMOUNT: ", amount.quotient())
	else:
		print(int(swapResults['data']['pool']['swaps'][0]['sqrtPriceX96'] ))
		print(swapAmount1.quotient())
		print(swapAmount1.currency.symbol)
		amount, p = pool.getOutputAmount(swapAmount1, int(swapResults['data']['pool']['swaps'][0]['sqrtPriceX96'] ))
		print(amount)
		print("SWAP AMOUNT: ", amount.quotient())
	#sys.exit()

	

getSwapDataFrame()
