import os, sys, warnings, setuptools, subprocess, shutil, platform, urllib, tempfile, ssl
from setuptools.command.install import install


assert platform.python_implementation() == "CPython", "ERROR: Python implementation must be CPython!."
assert sys.version_info > (3, 0, 0), "ERROR: Python version must be > 3.0!."
home = os.path.expanduser("~")
contexto = ssl.create_default_context()
contexto.check_hostname = False
contexto.verify_mode = ssl.CERT_NONE # Ignore SSL Errors and Warnings if any.


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


def prepare_folders():
  folders2create = (
    os.path.join(home, ".nimble"),
    os.path.join(home, ".nimble", "bin"),
    os.path.join(home, ".nimble", "pkgs"),
    os.path.join(home, ".choosenim"),
    os.path.join(home, ".choosenim", "channels"),
    os.path.join(home, ".choosenim", "downloads"),
    os.path.join(home, ".choosenim", "toolchains"),
    os.path.join(home, ".choosenim", "toolchains", "mingw64"),
    os.path.join(home, ".choosenim", "toolchains", "nim-#devel"),
  )
  for folder in folders2create:
    if not os.path.exists(folder):  # Older Python do not have exists_ok
      print("OK\tCreate folder: " + folder)
      os.makedirs(folder)
    else:
      warnings.warn("Folder already exists: " + folder)


def get_latest_stable_semver():
  try:
    print("OK\tHTTP GET http://nim-lang.org/channels/stable")
    result = urllib.request.urlopen("http://nim-lang.org/channels/stable", context=contexto).read().strip()
  except:
    result = "1.4.8"
    warnings.warn("Failed to fetch latest stable semver, fallback to " + result)
  print("OK\tLatest stable version: " + result)
  return result


def get_link(latest_stable_semver):
  assert len(latest_stable_semver) > 0, "latest_stable_semver must not be empty string"
  arch = 32 if not platform.machine().endswith("64") else 64  # https://stackoverflow.com/a/12578715
  if sys.platform.startswith("win"):
    return "http://nim-lang.org/download/nim-{}_x{}.zip".format(latest_stable_semver, arch)
  if sys.platform.startswith("linux"):
    return "http://nim-lang.org/download/nim-{}-linux_x{}.tar.xz".format(latest_stable_semver, arch)
  assert False, "Operating system currently not supported."


def download(url, path):
  with urllib.request.urlopen(url, context=contexto) as response:
    with open(path, 'wb') as outfile:
      shutil.copyfileobj(response, outfile)


def nim_setup(latest_stable_semver):
  # Basically this does the same as choosenim, but in pure Python,
  # so we dont need to "bundle" several choosenim EXEs, bash, etc.
  prepare_folders()
  latest_stable_link = get_link(latest_stable_semver)
  filename = os.path.join(tempfile.gettempdir(), latest_stable_link.split("/")[-1])
  print("OK\tDownloading: " + latest_stable_link)
  download(latest_stable_link, filename)
  print("OK\tDecompressing: " + filename)
  shutil.unpack_archive(filename, os.path.join(home, ".choosenim", "toolchains"))


def choosenim_setup():
  # We have to check if the user has choosenim already working.
  # Check for choosenim using "choosenim --version", to see if it is already installed,
  # if it is installed, run "choosenim update self" and "choosenim update stable",
  # if it is not installed just return.
  result = False
  shutil.rmtree(os.path.join(home, ".choosenim", "downloads"), ignore_errors=True)  # Clear download cache.
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
    result = True
  return result


def add_to_path(latest_stable_semver):
  # On Linux add Nim to the PATH.
  # Android does not have .bashrc equivalent.
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
  else:  # Windows
    finishexe = os.path.join(home, ".choosenim", "toolchains", "nim-" + latest_stable_semver, "finish.exe")
    if os.path.exists(finishexe):
      if subprocess.call(finishexe, shell=True) != 0:
        warnings.warn("Failed to run: " + finishexe)
      else:
        warnings.warn("Reboot to finish installation!")
    else:
      warnings.warn("File not found: " + finishexe)


def nimble_setup():
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
      if subprocess.call(nimble_cmd + " install cpython", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " install cpython")
      else:
        warnings.warn("Failed to run '" + nimble_cmd + " install cpython'")
      if subprocess.call(nimble_cmd + " install nodejs", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " install nodejs")
      else:
        warnings.warn("Failed to run '" + nimble_cmd + " install nodejs'")
      if subprocess.call(nimble_cmd + " install fusion", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " install fusion")
      else:
        warnings.warn("Failed to run '" + nimble_cmd + " install fusion'")
    else:
      warnings.warn("Failed to run '" + nimble_cmd + " refresh'")
  else:
    warnings.warn("File not found " + nimble_exe)
  return result


class X(install):

  def run(self):
    install.run(self)      # This is required by Python.
    if choosenim_setup():  # Check if choosenim is already installed.
      latest_stable_semver = get_latest_stable_semver() # Get latest semver.
      nim_setup(latest_stable_semver)                   # Install Nim.
      add_to_path(latest_stable_semver)                 # Add to PATH.
      if not self.nimble_setup():                       # Update Nimble.
        warnings.warn("Failed to setup Nimble")
    else:
      raise Exception(IOError, "Failed to install Nim")

setuptools.setup(
  name         = "choosenim_install",
  author       = "Juan_Carlos.nim",
  cmdclass     = {"install": X},
  author_email = "UNKNOWN",
  url          = "UNKNOWN",
)
