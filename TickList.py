class TickList
	def __init__(self, ticks, tickSpacing):
		self.ticks = ticks
		self.tickSpacing

	def isBelowSmallest(self, tickIdx):
		return tickIdx < self.ticks[0].tickIdx

	def isAtOrAboveLargest(self, tickIdx):
		return tickIdx >= self.ticks[-1].tickIdx

	def binarySearch(self, tickIdx):
		l = 0
		r = len(ticks) - 1
		i = 0
		while True:
			i = (l  + r) // 2

			if self.ticks[i].tickIdx and (i == len(self.ticks) - 1 or self.ticks[i+1].tickIdx > tickIdx):
				return i

			if self.ticks.tickIdx < tickIdx:
				l = i + 1
			else:
				r = i - 1


	def getTick(self, index):
		tick = self.ticks[self.binarySearch(index)]
		return tick

	def nextIniitializedTick(self, tickIdx, lte):
