import asyncio
import json
from collections import defaultdict, Counter
import pprint

import backoff
from aiofile import AIOFile

import modules.settings as settings
import utils as utils

class World():
	"""Handles loading, parsing, and saving of world data"""

	class Graph():
		"""Graph representation of world data"""

		def __init__(self):
			# key = a node, value = a list of connected nodes
			# Example: {(3000, 500): [(0, 50), (100, 500)]}
			self.edges = defaultdict(list)

			# key = a (from_node, to_node) tuple, value = distance between nodes
			# Example: {((3000, 500), (0, 50)): 1200}
			self.distances = {}

			# key = (x, y), value = a list of names for this node (len > 1 means intersection)
			self.named_nodes = defaultdict(list)

			# convenience structure for path finding algo
			self.nodes = set()

		def add_edge(self, from_node, to_node, distance):
			"""Adds nodes, edge, and distance data into the graph"""
			self.nodes.add(from_node)
			self.nodes.add(to_node)
			self.edges[from_node].append(to_node)
			self.edges[to_node].append(from_node)
			self.distances[(from_node, to_node)] = distance
			self.distances[(to_node, from_node)] = distance

		def add_node_name(self, node, label):
			"""Convenience method to build (x, y) -> name lookup table. 
			We use this when outputting waypoints along a path
			"""
			self.named_nodes[node].append(label)


	def __init__(self, controller):
		self.controller = controller
		# The world model. Gets updated and saved as crops get planted, etc.
		# Single source of truth
		self.model = {}

		self.graph = self.Graph()

	async def load(self):
		"""Fire async task to load the world file, which in turn parses it"""
		asyncio.create_task(self.load_file())

	async def parse_world(self):
		"""Parse world model into a graph for future use"""
		self.graph.add_node_name((0,0), 'charger')

		# Loop through paths and add waypoints to graph
		for path_name, path in self.model['paths'].items():
			try:
				waypoints = iter(path.items())
				prev_name, prev_coords = next(waypoints)
				prev_node = tuple(prev_coords)
			except StopIteration:
				print('Path missing waypoints? Returning.')
				return

			while True:
				self.graph.add_node_name(prev_node, f'{path_name}-{prev_name}')

				try:
					cur_name, cur_coords = next(waypoints)
					cur_node = tuple(cur_coords)
					distance = utils.distance(prev_node, cur_node)
					self.graph.add_edge(prev_node, cur_node, distance)

				except StopIteration:
					break

				prev_name, prev_coords, prev_node = cur_name, cur_coords, cur_node

		# Loop through fields and add rows as nodes to graph
		for field_name, field in self.model['fields'].items():
			try:
				rows = iter(field['rows'].items())
				prev_name, prev_data = next(rows)
				prev_node = tuple(prev_data['location'])
			except StopIteration:
				print('Field missing rows? Returning.')
				return
			except KeyError:
				print('Row missing location? Returning.')
				return

			while True:
				self.graph.add_node_name(prev_node, f'{field_name}-{prev_name}')

				try:
					cur_name, cur_data = next(rows)
					cur_node = tuple(cur_data['location'])
					distance = utils.distance(prev_node, cur_node)
					self.graph.add_edge(prev_node, cur_node, distance)

				except StopIteration:
					break

				prev_name, prev_data, prev_node = cur_name, cur_data, cur_node

	@backoff.on_exception(backoff.constant, OSError, interval=5)
	async def load_file(self, path=settings.WORLD_FILE_PATH):
		"""Loads and deserializes world JSON file into `self.model`

		@backoff decorator provides automatic retry every 5 seconds 
		if an OSError exception is raised. i.e. read fails
		"""

		async with AIOFile(path, 'r') as file:
			json_raw = await file.read()
			json_data = json.loads(json_raw)
			self.customer = json_data['customer']
			self.model = json_data['world']
			await self.parse_world()

	@backoff.on_exception(backoff.constant, OSError, interval=5)
	async def save_file(self, path=settings.WORLD_FILE_PATH):
		"""Serializes and writes `self.model` to world JSON file

		@backoff decorator provides automatic retry every 5 seconds 
		if an OSError exception is raised. i.e. write fails
		"""
		async with AIOFile(path, 'w') as file:
			json_data = { 'customer': self.customer, 'world': self.model }
			json_str = json.dumps(json_data, indent=4)
			await file.write(json_str)
	

