class TickList:
	def __init__(self, ticks, tickSpacing):
		self.ticks = ticks
		self.tickSpacing = tickSpacing

	def reset(self):
		for tick in self.ticks:
			tick.liquidityActive = 0
			tick.liquidityNet = 0
			tick.liquidityGross = 0
			tick.amount = 0
			tick.amount0 = 0
			tick.amount1 = 0
			tick.amountUSD = 0

	def isBelowSmallest(self, tickIdx):
		return tickIdx < self.ticks[0].tickIdx

	def isAtOrAboveLargest(self, tickIdx):
		return tickIdx >= self.ticks[-1].tickIdx

	def binarySearch(self, tickIdx):
		l = 0
		r = len(self.ticks) - 1
		i = 0
		while True:
			i = (l  + r) // 2

			if self.ticks[i].tickIdx and (i == len(self.ticks) - 1 or self.ticks[i+1].tickIdx > tickIdx):
				return i

			if self.ticks[i].tickIdx < tickIdx:
				l = i + 1
			else:
				r = i - 1


	def getTick(self, index):
		tick = self.ticks[self.binarySearch(index)]
		return tick

	def nextInitializedTick(self, tickIdx, lte):
		if lte:
			if self.isAtOrAboveLargest(tickIdx):
				return self.ticks[-1]

			index = self.binarySearch(tickIdx)
			return self.ticks[index]
		else:
			if self.isBelowSmallest(tickIdx):
				return self.ticks[0]
			index = self.binarySearch(tickIdx)
			return self.ticks[index + 1]

	def nextInitializedTickWithinOneWord(self, tickIdx, lte):
		compressed = tickIdx // self.tickSpacing
		if (lte):
			wordPos = compressed >> 8
			minimium = (wordPos << 8) * self.tickSpacing

			if self.isBelowSmallest(tickIdx):
				return (minimium, False)

			index = self.nextInitializedTick(tickIdx, lte).tickIdx
			nextInitializedTick = max(minimium, index)
			return (nextInitializedTick, (nextInitializedTick == index))
		else:
			wordPos = (compressed + 1) >> 8
			maximum = ((wordPos + 1) << 8) * self.tickSpacing - 1

			if self.isAtOrAboveLargest(tickIdx):
				return (maximum, False)

			index = self.nextInitializedTick(tickIdx, lte).tickIdx
			nextInitializedTick = min(maximum, index)
			return (nextInitializedTick, (nextInitializedTick == index))




