import os
class Constants:
	HOST_PATH=""
	VAR_PATH=""
	PLATFORM_PATH=""
	LOG_PATH=""
	COMMAND_FOR_ANSIBLE=""
	@staticmethod
	def setPath(username):	
		Constants.HOST_PATH='/root/training/'+username+'/hosts'
		Constants.VAR_PATH='/root/training/'+username+'/vars/vars.yml'
		Constants.COMMAND_FOR_ANSIBLE="ansible-playbook -i "+Constants.HOST_PATH+" " 
		Constants.LOG_PATH='/root/training/'+username+"log.txt"
