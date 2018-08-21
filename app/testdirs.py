import os
def loadFiles(username):
   for root,dirs,files in os.walk("/root/training/"+"chinmay.pawar"):
	for name in files:
		print "Dirs:::::::"+str(dirs)
		if name.endswith('playbook.yml'):
			print("/root/training/"+username+"/myplatform/"+name)



loadFiles("chinmay.pawar")
