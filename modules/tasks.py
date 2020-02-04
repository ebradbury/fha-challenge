import asyncio

class Tasks():
	"""Manages the task queue and task execution"""
	def __init__(self, controller):
		self.controller = controller

	async def load(self):
		"""Create task queue and enter consumer loop task"""
		self.queue = asyncio.Queue()
		asyncio.create_task(self.loop())

	async def loop(self):
		"""Infinitely await and execute tasks"""
		while True:
			task = await self.queue.get()
			await task.execute()
			self.queue.task_done()
			self.controller.input.print_prompt()

class Task():
	"""Represents an individual task"""
	def __init__(self, method, *args, **kwargs):
		self.method = method
		self.args = args
		self.kwargs = kwargs

	async def execute(self):
		return await self.method(*self.args, **self.kwargs)