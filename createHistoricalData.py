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

client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")

def getMintDataFrame():
	mintsDataFrame = pd.read_pickle("mints.pkl")
	# print(mintsDataFrame.iloc[-1])

	rowList = []
	firstTimestamp = mintsDataFrame.iloc[-1]['timestamp'] #1620169800 #int(mintsDataFrame.iloc[-1]['timestamp'])  #
	nextTimestamp = firstTimestamp + 30000
	while firstTimestamp < time.time():
		print(firstTimestamp - time.time())
		mintResults = mintBurnPull.getMints("asc", 300, firstTimestamp, nextTimestamp)
		if mintResults != "ERROR GETTING MINT DATA":
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
	firstTimestamp = burnsDataFrame.iloc[-1]['timestamp'] #1620169800  #int(burnsDataFrame.iloc[-1]['timestamp'])  #
	nextTimestamp = firstTimestamp + 30000
	while firstTimestamp < time.time():
		print(firstTimestamp - time.time())
		burnResults = mintBurnPull.getBurns("asc", 300, firstTimestamp, nextTimestamp)
		if burnResults != "ERROR":
			print("BENEJAO: ", burnResults)
			burns = burnResults['data']['pool']['burns']
			for burn in burns:
				newBurn = burn
				print(type(burn['amount']))
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
