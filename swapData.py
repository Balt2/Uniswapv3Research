from python_graphql_client import GraphqlClient
from Tick import * 
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/yekta/uniswap-v3-with-fees-and-amounts")

usdcUSDT = "0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf"
usdcETH = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
#poolAddress = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
#poolAddress = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
#poolAddress = "0x6c6bc977e13df9b0de53b251522280bb72383700"
poolAddress = usdcETH
numPreviousBlocks = 200


swapQuery = """
	query pool($poolAddress: String!) {
	    pool(id: $poolAddress) {
	      tick
	      token0 {
	      	id
	        symbol
	        decimals
	      }
	      token1 {
	      	id
	        symbol
	        decimals
	      }
	      feeTier
	      sqrtPrice
	      liquidity
	      swaps(
	      	first: 40
	      	orderBy: timestamp
	      	orderDirection: desc
	      ){
	      	amount0
	      	amount1
	      	amountUSD
	      	tick
	      	transaction{
	      		timestamp
	      		blockNumber
	      		gasPrice
	      	}
	      }
	    }
  }
"""

positionQuery = """

"""


swapData = client.execute(query=swapQuery, variables={"poolAddress": poolAddress})


token0 = Token(swapData['data']['pool']['token0']['id'], swapData['data']['pool']['token0']['symbol'], int(swapData['data']['pool']['token0']['decimals']) )

token1 = Token(swapData['data']['pool']['token1']['id'], swapData['data']['pool']['token1']['symbol'], int(swapData['data']['pool']['token1']['decimals']) )

swapDataArray = swapData['data']['pool']['swaps']

blockDict = {}

for swap in swapDataArray:
	blockNumber = int(swap['transaction']['blockNumber'])
	if blockNumber in blockDict:
		newSwap = Swap(token0, token1, float(swap['amountUSD']), float(swap['amount0']), float(swap['amount1']), float(swap['transaction']['gasPrice']), int(swap['tick']))
		blockDict[blockNumber].addSwap(newSwap)
	else:
		newSwap = Swap(token0, token1, float(swap['amountUSD']), float(swap['amount0']), float(swap['amount1']), float(swap['transaction']['gasPrice']), int(swap['tick']))
		blockDict[blockNumber] = Block(newSwap, blockNumber, int(swap['transaction']['timestamp']))

blockNums = list(blockDict.keys())
blockNums.sort()

x = []
totalusd = []
averageGas = []


for blockIndex in blockNums:
	block = blockDict[blockIndex]
	x.append(str(block.blockNumber))
	totalusd.append(block.totalUSD)
	averageGas.append(block.averageGas)
	print(block.blockNumber, " ", block.totalUSD)


# width = .8
# fig, ax = plt.subplots()

# ax.bar(list(map(lambda x : x - width/2, x)), totalusd, color='red', width = width, label = "Total USD")
# ax.tick_params(axis='y', labelcolor='red')

# # Generate a new Axes instance, on the twin-X axes (same position)
# ax2 = ax.twinx()

# # Plot exponential sequence, set scale to logarithmic and change tick color
# ax2.bar(list(map(lambda x : x + width/2, x)), averageGas, color='green', width = width, label = "Average Gas")
# ax2.tick_params(axis='y', labelcolor='green10)10
plt.figure(figsize=(12,8))
plt.bar(x, totalusd, width=.8, label="Total USD")
plt.xlabel("Block Number")
plt.ylabel("Total USD")
plt.title("Total Swap Value For Each Block")
plt.xticks(fontsize=7, rotation=75)
plt.legend()
plt.show()




#print(swapDataArray)