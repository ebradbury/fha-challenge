import asyncio
from math import inf
import pprint

class Path():
	"""Paths and routing"""

	def __init__(self, controller):
		self.controller = controller

	async def load(self):
		pass

	async def goto(self, destination):
		"""Make that rover move"""
		graph = self.controller.world.graph
		current_location = self.controller.rover.location
		
		# Get the shortest path to the destination as a list of waypoints
		path = await self.find_shortest_path(
			current_location,
			destination,
			graph
		)

		# "Move" along the path
		for node in path[1:]:
			self.controller.rover.location = node
			await asyncio.sleep(1) # simulate realistic speed

	async def find_shortest_path(self, from_node, to_node, graph):
		"""Dijkstra shortest path algorithm implementation"""

		# Fresh copy of all nodes
		nodes = graph.nodes.copy()
		# Tracks the shortest known distance to every node
		distances = {n: inf for n in nodes}
		# Stores the previous node, allows path construction
		breadcrumbs = {n: None for n in nodes}

		cur_node = from_node
		distances[from_node] = 0

		# Loop through all nodes
		while nodes:
			# Grab the node at the end of the shortest known path
			cur_node = min(nodes, key=lambda node: distances[node])
			nodes.remove(cur_node)

			# If we've reach the destination node, bail out
			if cur_node == to_node:
				break

			# Loop over the available neighbors their distances from cur_node
			for neighbor, distance in {n: graph.distances[(cur_node, n)] for n in graph.edges[cur_node]}.items():
				segment_sum = distances[cur_node] + distance
				# For each neighbor, check if it is a new shortest path to a node, store if so
				if segment_sum < distances[neighbor]:
					distances[neighbor] = segment_sum
					breadcrumbs[neighbor] = cur_node

		# Reconstruct the path in reverse
		path = [to_node]
		while breadcrumbs[cur_node] != None:
			path.append(breadcrumbs[cur_node])
			cur_node = breadcrumbs[cur_node]

		# Reverse to correct direction
		path.reverse()

		return path




