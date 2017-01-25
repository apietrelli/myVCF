from Tkinter import *
import os
import sys
import pip
import webbrowser
import time

platform = sys.platform

class App:
  def __init__(self, master):
    frame = Frame(master)
    frame.pack()
    self.button = Button(frame,
                         text="Run myVCF", fg="red",
                         command=self.run_app)
    self.button.pack(side=LEFT)
    self.slogan = Button(frame,
                         text="Stop myVCF",
                         command=self.stop_app)
    self.slogan.pack(side=LEFT)
    self.slogan = Button(frame,
                         text="Install packages",
                         command=self.install_packages)
    self.slogan.pack(side=LEFT)
  def run_app(self):
      print("Running myVCF...")
      if platform == "win32":
          os.system("python manage.py runserver &") 
      else:
          os.system("python manage.py runserver &")
      print("myVCF page is opening in the browser...")
      time.sleep(2)
      url = "http://localhost:8000/"
      webbrowser.open(url,new=2)
      return True

  def stop_app(self):
      print("Stopping myVCF...")
      if platform == "win32":
          # Windows command to
          pass
      else:
          os.system('pkill -f "python manage.py runserver"')
      print "myVCF is shoutdown"

  def install_packages(self):
      def install(requirements):
          pip.main(['install', '--user', '-r', requirements])
      try:
          print("Installing Python requirements...")
          req = "requirements.txt"
          install(req)
          print "All libraries are installed \nClick on Run myVCF button to run the App"
      except:
          print "Unable to install %s using pip. Please read the instructions for \
                  manual installation.. Exiting" % req
          return False




root = Tk()
root.title('myVCF GUI')
app = App(root)
root.mainloop()
