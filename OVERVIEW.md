# Overview

Rough functionality:
- User
	- (id) -> profile
	- signup
		- Create a team
		- Or join a team
	- login
	- logout
- Team
	- (id) -> profile
	- clear (NEW)
		- Stops all running containers associated with the team
- CTF
	- (id) -> Get CTF info
	- start
		- Check if team has already completed it
		- Only if no container is assigned to the team before
			- If container exists, return its CTF ID
		- Else
			- Start the container
			- Save container and CTF ID to team profile
	- stop
		- Stop container and delete record from DB
	- hints/(1,2,3,...)
		- As hints are used, save their usage to their team profile
	- flag
		- If flag invalid, return flag invalid
		- If valid, check for hints used and assign necessary points.
	- add (TBD)
		- Make a dynamic way to add CTFs
- Admin
    - TBD
