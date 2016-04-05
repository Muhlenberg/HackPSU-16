# HackPSU-16
Project for hackathon at PennState 2016

This project should be easily extensible to multiple natural and programming languages, and will be structured to support that

Below is the project outline

## PROJECT NAME

	start - initialize speech recognizer, focus subl window

	loop - get voice command

		- parse into string (e.g. "build", "class", "_name_")

		- execute command in sublime

	endloop

	end - subl closes



parse(data)

	lookup keyword in dictionary (e.g. "build", "make", "create")

	identify subject ("class", "method", "variable")

	identify parameters ("public", "private", type)

	construct standardized command sequence


execute(command_sequence)

	read in config file, use appropriate settings
	
	apply settings using sublime text api, and insert necessary text
