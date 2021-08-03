from python_graphql_client import GraphqlClient
#client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/yekta/uniswap-v3-with-fees-and-amounts")
client = GraphqlClient(endpoint="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")

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

def getMints(direction, numberEvents, timeStampGTE = 0, timeStampLT = 1720169800):
	getMints = """
			query getMints($poolAddress: String!, $numberEvents: Int, $direction: String, $timeStampGTE: Int, $timeStampLT: Int) {
			    pool(id: $poolAddress) {
				mints(
					first: $numberEvents
					skip: $skip
					orderBy: timestamp
		      		orderDirection: $direction
		      		where: {timestamp_gte: $timeStampGTE, timestamp_lt: $timeStampLT}
				){
					id
					timestamp
					owner
					sender
					origin
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

	try:
		mintResults = client.execute(query=getMints, variables={"poolAddress": poolAddress, "numberEvents": numberEvents, "skip": 1, "direction": direction, "timeStampGTE": timeStampGTE, "timeStampLT": timeStampLT})
	except:
		return "ERROR"

	if 'data' not in mintResults.keys():
		return "ERROR"

	return mintResults

def getBurns(direction, numberEvents, timeStampGTE = 0, timeStampLT = 1720169800):
	getBurns = """
			query getBurns($poolAddress: String!, $numberEvents: Int, $direction: String, $timeStampGTE: Int, $timeStampLT: Int) {
			    pool(id: $poolAddress) {
				burns(
					first: $numberEvents
					skip: $skip
					orderBy: timestamp
		      		orderDirection: $direction
		      		where: {timestamp_gte: $timeStampGTE, timestamp_lt: $timeStampLT}

				){
					timestamp
					owner
					origin
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
	try:
		burnResults = client.execute(query=getBurns, variables={"poolAddress": poolAddress, "numberEvents": numberEvents, "skip": 1, "direction": direction, "timeStampGTE": timeStampGTE, "timeStampLT": timeStampLT})
	except:
		return "ERROR"

	if 'data' not in burnResults.keys():
		return "ERROR"

	return burnResults

def getAverageTransactionFee():
	mintResults = getMints("desc", numberPreviousEvents//2)
	burnResults = getBurns("desc", numberPreviousEvents//2)
	mintResultsArray = mintResults['data']['pool']['mints']
	burnResultsArray = burnResults['data']['pool']['burns']
	totalTransactionFees = 0
	for i in range(len(mintResultsArray)):
		totalTransactionFees += getTransactionFee(mintResultsArray[i]['transaction']['gasPrice'], mintResultsArray[i]['transaction']['gasUsed'])
		totalTransactionFees += getTransactionFee(burnResultsArray[i]['transaction']['gasPrice'], burnResultsArray[i]['transaction']['gasUsed'])

	averageTransactionFee = totalTransactionFees / numberPreviousEvents
	return averageTransactionFee
