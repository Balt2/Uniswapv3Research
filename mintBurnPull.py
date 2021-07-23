from python_graphql_client import GraphqlClient
client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/yekta/uniswap-v3-with-fees-and-amounts")


usdcUSDT = "0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf"
usdcETH = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
wbtcETH = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
daiUSDC = "0x6c6bc977e13df9b0de53b251522280bb72383700"
mmUSDC = "0x84383fb05f610222430f69727aa638f8fdbf5cc1"
shibETH = "0x5764a6f2212d502bc5970f9f129ffcd61e5d7563"
#poolAddress = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
#poolAddress = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"
#poolAddress = "0x6c6bc977e13df9b0de53b251522280bb72383700"
poolAddress = usdcETH

numberPreviousEvents = 20


def getTransactionFee(gasPrice, gasLimit):
	gasPriceEth = float(gasPrice) * 1/(10 ** 18)
	return gasPriceEth * float(gasLimit)


def getAverageTransactionFee():


	getMints = """
			query getMints($poolAddress: String!, $numberEvents: Int) {
			    pool(id: $poolAddress) {
				mints(
					first: $numberEvents
					skip: $skip
					orderBy: timestamp
		      		orderDirection: desc
				){
					timestamp
					amount
					amount0
					amount1
					amountUSD
					tickLower
					tickUpper
					transaction {
						blockNumber
						gasUsed
						gasPrice
						}
				
				}
			}
		}

		"""

	getBurns = """
			query getBurns($poolAddress: String!, $numberEvents: Int) {
			    pool(id: $poolAddress) {
				burns(
					first: $numberEvents
					skip: $skip
					orderBy: timestamp
		      		orderDirection: desc
				){
					timestamp
					amount
					amount0
					amount1
					amountUSD
					tickLower
					tickUpper
					transaction {
						blockNumber
						gasUsed
						gasPrice
					}
					
				}
			}
		}

		"""

	mintResults = client.execute(query=getMints, variables={"poolAddress": poolAddress, "numberEvents": numberPreviousEvents//2, "skip": 1})

	burnResults = client.execute(query=getBurns, variables={"poolAddress": poolAddress, "numberEvents": numberPreviousEvents//2, "skip": 1})


	mintResultsArray = mintResults['data']['pool']['mints']
	burnResultsArray = burnResults['data']['pool']['burns']
	totalTransactionFees = 0
	for i in range(len(mintResultsArray)):
		totalTransactionFees += getTransactionFee(mintResultsArray[i]['transaction']['gasPrice'], mintResultsArray[i]['transaction']['gasUsed'])
		totalTransactionFees += getTransactionFee(burnResultsArray[i]['transaction']['gasPrice'], burnResultsArray[i]['transaction']['gasUsed'])

	averageTransactionFee = totalTransactionFees / numberPreviousEvents
	return averageTransactionFee
