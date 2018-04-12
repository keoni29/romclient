from subprocess import Popen

class Emulator():
  emulatorPath = 'stella'

  def __init__(self):
    pass

  def launch(self, args):
      cmd = self.emulatorPath
      if cmd and args:
        self.emulatorProcess = Popen([cmd, args])


  def terminate(self):
    if self.emulatorProcess:
      self.emulatorProcess.terminate()