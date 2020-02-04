import sys, re
import asyncio

class Input:
	"""Handles command shell input"""
	def __init__(self, controller):
		self.controller = controller
		self.commands = {}

		self.register_command(
			'help',
			'usage: `help` or `help <command>`\nPrints this help text or <command> help if given',
			self.print_help
		)

	async def load(self):
		# Sets up asynchronous stdin reader
		loop = asyncio.get_running_loop()
		loop.add_reader(sys.stdin, self.handle_input)

		self.print_prompt()

	def register_command(self, name, usage, callback):
		self.commands[name] = {'usage': usage, 'callback': callback}

	def handle_input(self):
		"""Called when stdin is available. i.e. command is entered

		Calls the command callback if it exists
		"""

		line = sys.stdin.readline().strip()

		if line == '':
			# print('')
			self.print_prompt()
			return

		command_name, *parts = line.split()

		if command_name in self.commands:
			# Call given command and unpack parts into args
			self.commands[command_name]['callback'](*parts)
		else:
			print(command_name + ' : command not found')
			self.print_available_commands()


		self.print_prompt()

	def print_prompt(self):
		sys.stdout.write('>> ')
		sys.stdout.flush()

	def print_help(self, command=None, *args, **kwargs):
		if command:
			if command in self.commands:
				print(self.commands[command]['usage'])
			else:
				print(f'{command} : unknown command')
		else:
			print(self.commands['help']['usage'])

		self.print_available_commands()

	def print_available_commands(self):
		print('\nAvailable commands:')
		for name, command in self.commands.items():
			print(f'\t{name}')


