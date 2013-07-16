__author__="WISEKEY\mdalbuquerque"
__date__ ="$Sep 24, 2012 4:04:04 PM$"

from setuptools import setup,find_packages

setup (
  name = 'P2P',
  version = '0.1',
  packages = find_packages(),

  # Declare your packages' dependencies here, for eg:
  install_requires=['foo>=3'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'WISEKEY\mdalbuquerque',
  author_email = '',

  summary = 'Just another Python package for the cheese shop',
  url = '',
  license = '',
  long_description= 'Long description of the package',

  # could also include long_description, download_url, classifiers, etc.

  
)


def execute_cmd(cmd_string):
    system("clear")
    a = system(cmd_string)
    print ""
    if a == 0:
        print "Command executed correctly"
    else:
        print "Command terminated with error"
    raw_input("Press enter")
    print ""

     if x == str('1'):
          username = get_param("Enter the username")
          homedir = get_param("Enter the home directory, eg /home/nate")
          groups = get_param("Enter comma-separated groups, eg adm,dialout,cdrom")
          shell = get_param("Enter the shell, eg /bin/bash:")
          curses.endwin()
          execute_cmd("useradd -d " + homedir + " -g 1000 -G " + groups + " -m -s " + shell + " " + username)
     
     if x == ord('2'):
          curses.endwin()
          execute_cmd("apachectl restart")
     
     if x == ord('3'):
          curses.endwin()
          execute_cmd("df -h")
          
               
     username = get_param("Enter the username")
     homedir = get_param("Enter the home directory, eg /home/nate")
     groups = get_param("Enter comma-separated groups, eg adm,dialout,cdrom")
     shell = get_param("Enter the shell, eg /bin/bash:")

     # execute_cmd("useradd -d " + homedir + " -g 1000 -G " + groups + " -m -s " + shell + " " + username)