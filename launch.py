import asyncio

from controller import Controller

def main():
	"""Entry point

	Initializes the controller and enters the main loop
	"""
	controller = Controller()
	loop = asyncio.get_event_loop()
	loop.create_task(controller.load())
	loop.run_forever()

if __name__ == '__main__':
	main()
