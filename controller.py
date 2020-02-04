import sys
import asyncio

from modules.input import Input
from modules.world import World
from modules.rover import Rover
from modules.path import Path
from modules.tasks import Tasks

class Controller:
	"""Controller class

	The Controller class initializes all of the modules and sets 
	up the interactive python shell.
	"""

	def __init__(self):
		# Initialize modules
		self.input = Input(self)
		self.world = World(self)
		self.rover = Rover(self)
		self.path = Path(self)
		self.tasks = Tasks(self)

		self.shell_banner = 'Now in Python shell\nController instance available as `self`\nExit with Ctrl-D'

		self.input.register_command(
			'exit',
			'usage: `exit`\nExits the program',
			self.cmd_exit
		)
		self.input.register_command(
			'shell',
			'usage: `shell`\nOpens an interactive python shell within the controller context',
			self.make_shell_cmd(locals())
		)

	async def load(self):
		await self.input.load()
		await self.world.load()
		await self.rover.load()
		await self.path.load()
		await self.tasks.load()

	def cmd_exit(self):
		print('Exiting')
		sys.exit()

	def make_shell_cmd(self, locals):
		"""Returns a closure that opens a Python shell with `locals` available when called"""
		def cmd_shell():
			import code
			code.interact(banner=self.shell_banner, local=locals, exitmsg='Returning to command shell...')

		return cmd_shell
