import os, sys, warnings, setuptools, subprocess, shutil
from setuptools.command.install import install


assert sys.version_info > (3, 0, 0), "ERROR: Python version must be > 3.0!."
os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
home = os.path.expanduser("~")


def which(cmd, mode = os.F_OK | os.X_OK, path = None):
  # shutil.which is Python 3.3+ only.
  def _access_check(fn, mode):
    return (os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn))

  if _access_check(cmd, mode):
    return cmd
  path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)
  if sys.platform == "win32":
    if os.curdir not in path:
      path.insert(0, os.curdir)
    pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
    matches = [cmd for ext in pathext if cmd.lower().endswith(ext.lower())]
    files = [cmd] if matches else [cmd + ext.lower() for ext in pathext]
  else:
    files = [cmd]
  seen = set()
  for dir in path:
    dir = os.path.normcase(dir)
    if dir not in seen:
      seen.add(dir)
      for thefile in files:
        name = os.path.join(dir, thefile)
        if _access_check(name, mode):
          return name
  warnings.warn("shutil.which can not find executable " + cmd)
  return cmd


class X(install):

  def nimble_setup(self):
    # After choosenim, we check that Nimble is working,
    # as "nimble" or "~/.nimble/bin/nimble", then install nimpy and fusion
    result = False
    ext = ".exe" if sys.platform.startswith("win") else ""
    nimble_exe = which("nimble" + ext)  # Try "nimble"
    if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
      nimble_exe = os.path.join(home, '.nimble', 'bin', "nimble" + ext)  # Try full path to "nimble"
      if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
        nimble_exe = "nimble"
        if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
          warnings.warn("Nim not found, tried 'nimble' and " + nimble_exe)
    nim_exe = which("nim" + ext)  # Ask which for "nim"
    if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
      nim_exe = os.path.join(home, '.nimble', 'bin', "nim" + ext)  # Try full path to "nim"
      if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
        nim_exe = "nim"
        if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
          warnings.warn("Nim not found, tried 'nim' and " + nim_exe)
    if os.path.exists(nimble_exe):
      nimble_cmd = nimble_exe + " -y --noColor --nim:'" + nim_exe + "'"
      if subprocess.call(nimble_cmd + " refresh", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " --verbose refresh")
        if subprocess.call(nimble_cmd + " install nimpy", shell=True, timeout=999) == 0:
          print("OK\t" + nimble_cmd + " install nimpy")
          if subprocess.call(nimble_cmd + " install fusion", shell=True, timeout=999) == 0:
            print("OK\t" + nimble_cmd + " install fusion")
            result = True
          else:
            warnings.warn("Failed to run '" + nimble_cmd + " install fusion'")
        else:
          warnings.warn("Failed to run '" + nimble_cmd + " install nimpy'")
      else:
        warnings.warn("Failed to run '" + nimble_cmd + " refresh'")
    else:
      warnings.warn("File not found " + nimble_exe)
    return result

  def choosenim_setup(self):
    # Check for choosenim using "choosenim --version", to see if it is already installed,
    # if it is installed, run "choosenim update self" and "choosenim update stable",
    # if it is not installed run "init.sh" or "choosenim --firstInstall" to install choosenim.
    result = False
    choosenim_exe = "choosenim.exe" if sys.platform.startswith("win") else "choosenim"
    if subprocess.call(choosenim_exe + " --version", shell=True, timeout=999) == 0:
      warnings.warn("Choosenim is already installed and working on the system " + choosenim_exe)
      if subprocess.call(choosenim_exe + " update self", shell=True, timeout=999) != 0:
        warnings.warn("Failed to run '" + choosenim_exe + " update self'")  # Dont worry if "update self" fails.
      if subprocess.call(choosenim_exe + " update stable", shell=True, timeout=999) == 0:
        result = True
      else:
        warnings.warn("Failed to run '" + choosenim_exe + " update stable'")
    else:
      choosenim_exe = os.path.join(os.path.dirname(__file__), "choosenim.exe") if sys.platform.startswith("win") else "init.sh"
      if os.path.exists(choosenim_exe):
        exe_prefix = '' if sys.platform.startswith('win') else 'sh '
        exe_params = ' --yes --verbose --noColor --firstInstall stable' if sys.platform.startswith('win') else ' -y'
        choosenim_cmd = exe_prefix + choosenim_exe + exe_params
        if subprocess.call(choosenim_cmd, shell=True, timeout=999) == 0:
          print("OK\t" + choosenim_cmd)
          if sys.platform.startswith('win'):
            if subprocess.call(choosenim_exe + " stable --firstInstall", shell=True, timeout=999) == 0:
              result = True
          else:
            result = True
        else:
          warnings.warn("Failed to run " + choosenim_cmd)
      else:
        warnings.warn("File not found " + choosenim_exe)
      shutil.rmtree(os.path.join(home, ".choosenim", "downloads"), ignore_errors=True)  # Clear download cache.
    return result

  def add_to_path(self):
    # On Linux add Nim to the PATH.
    if not sys.platform.startswith("win"):
      new_path = "export PATH=" + os.path.join(home, '.nimble/bin') + ":$PATH"
      filename = os.path.join(home, ".bashrc")
      try:
        if filename.exists():
          found = False
          with open(filename, "a") as f:
            for line in f:
              if new_path == line:
                found = True
            if not found:
              f.write(new_path)
        else:
          with open(filename, "w") as f:
            f.write(new_path)
        print("OK\t" + filename)
      except:
        warnings.warn("Failed to write file: " + filename)
      filename = os.path.join(home, ".profile")
      try:
        if filename.exists():
          found = False
          with open(filename, "a") as f:
            for line in f:
              if new_path == line:
                found = True
            if not found:
              f.write(new_path)
        else:
          with open(filename, "w") as f:
            f.write(new_path)
        print("OK\t" + filename)
      except:
        warnings.warn("Failed to write file ~/.profile")
      filename = os.path.join(home, ".bash_profile")
      try:
        if filename.exists():
          found = False
          with open(filename, "a") as f:
            for line in f:
              if new_path == line:
                found = True
            if not found:
              f.write(new_path)
        else:
          with open(filename, "w") as f:
            f.write(new_path)
        print("OK\t" + filename)
      except:
        warnings.warn("Failed to write file ~/.bash_profile")
      filename = os.path.join(home, ".zshrc")
      try:
        if filename.exists():
          found = False
          with open(filename, "a") as f:
            for line in f:
              if new_path == line:
                found = True
            if not found:
              f.write(new_path)
        else:
          with open(filename, "w") as f:
            f.write(new_path)
        print("OK\t" + filename)
      except:
        warnings.warn("Failed to write file ~/.zshrc")
      # https://github.com/juancarlospaco/choosenim_install/issues/4
      filename = os.path.join(home, ".zshenv")
      try:
        if filename.exists():
          found = False
          with open(filename, "a") as f:
            for line in f:
              if new_path == line:
                found = True
            if not found:
              f.write(new_path)
        else:
          with open(filename, "w") as f:
            f.write(new_path)
        print("OK\t" + filename)
      except:
        warnings.warn("Failed to write file ~/.zshenv")

  def run(self):
    install.run(self)
    # TODO: nimble has a new "--noSSLCheck" that can be added in the future.
    if self.choosenim_setup():
      if self.nimble_setup():
        self.add_to_path()
      else:
        warnings.warn("Failed to setup Nimble")
    else:
      raise Exception(IOError, "Failed to install choosenim")

setuptools.setup(
  name         = "choosenim_install",
  author       = "Juan_Carlos.nim",
  cmdclass     = {"install": X},
  author_email = "UNKNOWN",
  url          = "UNKNOWN",
)
