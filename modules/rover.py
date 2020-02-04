import asyncio
from modules.tasks import Task

class Rover:
	"""Represents the rover itself

	Provides `goto` and `plant` commands. Outputs location every second as it changes
	"""

	def __init__(self, controller):
		self.controller = controller
		self._location = (0,0)

		self.goto_usage = 'usage: `goto <location>` where <location> is \'charger\' or a field and row (e.g. `goto field A row 10`)'
		self.controller.input.register_command(
			'goto',
			self.goto_usage,
			self.cmd_goto
		)

		self.plant_usage = 'usage: `plant <crop> in field <field> row <row>`. (e.g. `plant BEETS in field A row 4`)'
		self.controller.input.register_command(
			'plant',
			self.plant_usage,
			self.cmd_plant
		)

	@property
	def location(self):
		return self._location
	
	@location.setter
	def location(self, value):
		self._location = value
		self.location_queue.put_nowait(value)

	async def load(self):
		# We push "state" (just location for now) into this queue and
		# consume it in emit_rover_state every second.
		self.location_queue = asyncio.Queue()
		asyncio.create_task(self.emit_rover_state())

	async def emit_rover_state(self):
		while True:
			location = await self.location_queue.get()
			print(location, self.controller.world.graph.named_nodes[location])
			# Great place to send state off to a logging web API 
			await asyncio.sleep(1)

	def cmd_goto(self, *args):
		"""Validate destination and add the goto task to the queue"""
		argc = len(args)

		if not argc:
			print('missing required arguments')
			print(self.goto_usage)
			return

		world = self.controller.world.model

		if args[0] == 'charger':
			destination = tuple(world['charger']['location'])
		elif args[0] == 'field':
			try:
				field = args[1].lower()
				row = f'{int(args[3]):02d}'
			except IndexError:
				print('missing required arguments')
				print(self.goto_usage)
				return
			
			try:
				destination = tuple(world['fields'][f'field-{field}']['rows'][f'row-{row}']['location'])
			except KeyError:
				print('that field or row doesn\'t exist')
				return

		else:
			print('missing required arguments')
			print(self.goto_usage)
			return

		self.controller.tasks.queue.put_nowait(Task(self.controller.path.goto, destination))

	def cmd_plant(self, *args):
		"""Validate field/row and add the task to the queue"""
		argc = len(args)

		if argc < 6:
			print('missing required arguments')
			print(self.plant_usage)
			return

		try:
			crop = args[0]
			field = args[3].lower()
			row = f'{int(args[5]):02d}'
		except IndexError:
			print('missing required arguments')
			print(self.plant_usage)
			return
		
		try:
			world = self.controller.world.model
			destination = world['fields'][f'field-{field}']['rows'][f'row-{row}']
		except KeyError:
			print('that field or row doesn\'t exist')
			return

		self.controller.tasks.queue.put_nowait(Task(self.plant, crop, field, row))

	async def plant(self, crop, field, row):
		"""Plant task. Moves the rover to the destination, plants the crop, then persists the changes to disk"""
		field_row = self.controller.world.model['fields'][f'field-{field}']['rows'][f'row-{row}']
		destination = tuple(field_row['location'])
		await self.controller.path.goto(destination)
		self.controller.world.model['fields'][f'field-{field}']['rows'][f'row-{row}']['crop'] = crop
		await self.controller.world.save_file()
		print(f'successfully planted {crop} in field-{field} row-{row}')




