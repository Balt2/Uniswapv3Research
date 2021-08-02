from python_graphql_client import GraphqlClient
from Tick import *
import matplotlib.pyplot as plt
from SqrtPriceMath import *
from TickList import *
import constants

client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")
usdcETH = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"
poolAddress = usdcETH

pairData = """
		query pair($poolAddress: String!) {
		    pair(id: $poolAddress) {
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
		      reserveUSD
		      volumeUSD
		      liquidityProviderCount
		    }
	  }
	"""


swapQuery = """
	query swaps($poolAddress: String!) {
	   transactions(first: 400, orderBy: blockNumber, orderDirection: desc) {
	    swaps(where: {pair:"0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"} ){
	      amountUSD
	      amount0In
	      amount1In
	      amount0Out
	      amount0In
	      transaction{
	        blockNumber
	        timestamp
	      }
	    }
	  } 
  }
"""


def getReserveUSD():
	pairDataQuery = client.execute(query=pairData, variables={"poolAddress": poolAddress} )
	reserveUSD = float(pairDataQuery['data']['pair']['reserveUSD'])
	return reserveUSD

def getSwaps():
	swapsReturn = []
	swapQueryData = client.execute(query=swapQuery, variables={"poolAddress": poolAddress} )
	swaps = swapQueryData['data']['transactions']
	for swap in swaps:
		if swap != {'swaps': []}:
			for s in swap['swaps']:
				newSwap = Swap(0, 0, float(s['amountUSD']), 0, 0, 0, 0, int(s['transaction']['blockNumber'])) 
				swapsReturn.append(newSwap)
	return swapsReturn



getSwaps()

