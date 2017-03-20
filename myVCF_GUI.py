from Tkinter import *
import os
import sys
import webbrowser
import time

platform = sys.platform
python_bin = sys.executable
path = os.path.dirname(__file__)
# Go to myVCF dir
os.chdir(path)

try:
    import pip
except ImportError:
    os.system(python_bin +" lib/get-pip.py")
    import pip


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
          os.system("START /B "+ python_bin + " manage.py runserver")
          #print("START /B "+ python_bin +" manage.py runserver")
          time.sleep(4)
      else:
          #os.system("echo " + python_bin)
          os.system(python_bin + " manage.py runserver &")
          time.sleep(2)
      print("myVCF page is opening in the browser...")
      url = "http://localhost:8000/"
      webbrowser.open(url,new=2)
      return True

  def stop_app(self):
      print("Stopping myVCF...")
      if platform == "win32":
          os.system("taskkill /F /IM python.exe")
      else:
          os.system('pkill -f "python manage.py runserver"')
      print "myVCF is shoutdown"

  def install_packages(self):
      def install(requirements):
          pip.main(['install', '--user', '-r', requirements])
      try:
          print("Installing Python requirements...")
          if platform == "win32":
            req = path + "\\requirements.txt"
          else:
            req = path + "/requirements.txt"
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
