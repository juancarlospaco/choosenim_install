import os, sys, setuptools, subprocess, shutil, platform, urllib, tempfile, ssl, json
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
  print("ER\tshutil.which can not find executable " + cmd)
  return cmd


def prepare_folders():
  folders2create = [
    os.path.join(home, ".local"),
    os.path.join(home, ".local", "bin"),
    os.path.join(home, ".nimble"),
    os.path.join(home, ".nimble", "pkgs"),
    os.path.join(home, ".nimble", "bin"),
    os.path.join(home, ".choosenim"),
    os.path.join(home, ".choosenim", "channels"),
    os.path.join(home, ".choosenim", "downloads"),
    os.path.join(home, ".choosenim", "toolchains"),
  ]
  for folder in folders2create:
    if not os.path.exists(folder):  # Older Python do not have exists_ok
      print("OK\tCreate folder: " + folder)
      os.makedirs(folder)
    else:
      print("ER\tFolder already exists: " + folder)


def download(url, path):
  with urllib.request.urlopen(url, context=contexto) as response:
    with open(path, 'wb') as outfile:
      shutil.copyfileobj(response, outfile)


def get_link():
  arch = 32 if not platform.machine().endswith("64") else 64  # https://stackoverflow.com/a/12578715
  result = None
  if sys.platform.startswith("linux"):
    result = "https://github.com/nim-lang/nightlies/releases/download/latest-devel/linux_x{}.tar.xz".format(arch)
  elif sys.platform.startswith("win"):
    result = "https://github.com/nim-lang/nightlies/releases/download/latest-devel/windows_x{}.zip".format(arch)
  elif sys.platform.startswith("darwin"):
    result = "https://github.com/nim-lang/nightlies/releases/download/latest-devel/macosx_x{}.tar.xz".format(arch)
  assert result is not None, "Operating system or hardware architecture not supported or download not available or unkown network error."
  return result


def nim_setup():
  # Basically this does the same as choosenim, but in pure Python,
  # so we dont need to "bundle" several choosenim EXEs, bash, etc.
  prepare_folders()
  latest_stable_link = get_link()
  filename = os.path.join(tempfile.gettempdir(), latest_stable_link.split("/")[-1])
  print("OK\tDownloading: " + latest_stable_link)
  download(latest_stable_link, filename)
  print("OK\tDecompressing: " + filename + " into " + os.path.join(home, ".choosenim", "toolchains", "nim-#devel"))
  shutil.unpack_archive(filename, os.path.join(home, ".choosenim", "toolchains"))
  for folder in os.listdir(os.path.join(home, ".choosenim", "toolchains")):
    if folder.lower().startswith("nim-"):
      print("OK\tCopying: " + os.path.join(home, ".choosenim", "toolchains", folder) + " into " + os.path.join(home, ".choosenim", "toolchains", "nim-#devel"))
      os.rename(
        os.path.join(home, ".choosenim", "toolchains", folder),
        os.path.join(home, ".choosenim", "toolchains", "nim-#devel"))
      break
  try:
    print("OK\tCopying: " + os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin") + " into " + os.path.join(home, ".nimble", "bin"))
    shutil.copytree(
      os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin"),
      os.path.join(home, ".nimble", "bin"))
    shutil.copytree(  # I dunno why Nimble wants this sometimes.
      os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "lib"),
      os.path.join(home, ".nimble", "lib"))

    if sys.platform.startswith("linux"):
      print("OK\tCopying: " + os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin") + " into " + os.path.join(home, ".local", "bin"))
      shutil.copytree(
        os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin"),
        os.path.join(home, ".local", "bin"))
    elif sys.platform.startswith("darwin"):
      print("OK\tCopying: " + os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin") + " into " + os.path.join(home, "bin"))
      shutil.copytree(
        os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin"),
        os.path.join(home, "bin"))

    shutil.copytree(
      os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin"),
      os.path.join(home, ".nimble", "lib"))

  except:
    print("ER\tFailed to copy binaries into folder: " + os.path.join(home, ".nimble", "bin"))


def choosenim_setup():
  # We have to check if the user has choosenim already working.
  # Check for choosenim using "choosenim --version", to see if it is already installed,
  # if it is installed, run "choosenim update self" and "choosenim update stable",
  # if it is not installed just return.
  result = False
  shutil.rmtree(os.path.join(home, ".choosenim", "downloads"), ignore_errors=True)  # Clear download cache.
  choosenim_exe = "choosenim.exe" if sys.platform.startswith("win") else "choosenim"
  if subprocess.call(choosenim_exe + " --version", shell=True, timeout=999) == 0:
    print("ER\tChoosenim is already installed and working on the system " + choosenim_exe)
    if subprocess.call(choosenim_exe + " update self", shell=True, timeout=999) != 0:
      print("ER\tFailed to run '" + choosenim_exe + " update self'")  # Dont worry if "update self" fails.
    if subprocess.call(choosenim_exe + " update stable", shell=True, timeout=999) == 0:
      result = True
    else:
      print("ER\tFailed to run '" + choosenim_exe + " update stable'")
  else:
    result = True
  return result


def add_to_path(filename):
  new_path = "export PATH=" + os.path.join(home, ".nimble", "bin") + ":" + os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin") + ":$PATH"
  filename = os.path.join(home, filename)
  try:
    found = False
    with open(filename, "a") as f:
      for line in f:
        if new_path == line:
          found = True
      if not found:
        print("OK\tAppending to " + filename)
        f.write(new_path)
  except:
    print("OK\tWriting to " + filename)
    with open(filename, "w") as f:
      f.write(new_path)


def run_finishexe():
  finishexe = os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin", "finish.exe")
  if os.path.exists(finishexe):
    if subprocess.call(finishexe, shell=True) != 0:
      print("ER\tFailed to run: " + finishexe)
    else:
      print("ER\tReboot to finish installation!")
  else:
    print("ER\tFile not found: " + finishexe)


def nimble_setup():
  # After choosenim, we check that Nimble is working,
  # as "nimble" or "~/.nimble/bin/nimble", then install nimpy and fusion
  result = False
  ext = ".exe" if sys.platform.startswith("win") else ""
  nimble_exe = os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin", "nimble" + ext)
  if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
    nimble_exe = os.path.join(home, '.nimble', 'bin', "nimble" + ext)  # Try full path to "nimble"
    if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
      nimble_exe = "nimble"
      if subprocess.call(nimble_exe + " --version", shell=True, timeout=99) != 0:
        print("ER\tNim not found, tried 'nimble' and " + nimble_exe)
  nim_exe = os.path.join(home, ".choosenim", "toolchains", "nim-#devel", "bin", "nim" + ext)
  if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
    nim_exe = os.path.join(home, '.nimble', 'bin', "nim" + ext)  # Try full path to "nim"
    if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
      nim_exe = "nim"
      if subprocess.call(nim_exe + " --version", shell=True, timeout=99) != 0:
        print("ER\tNim not found, tried 'nim' and " + nim_exe)
  if os.path.exists(nimble_exe):
    new_path = "PATH=" + os.path.join(home, ".nimble", "bin") + ":$PATH"
    nimble_cmd = nimble_exe + " --accept --noColor --noSSLCheck --nim=" + nim_exe
    if subprocess.call(nimble_cmd + " refresh", shell=True, timeout=999) == 0:
      print("OK\t" + nimble_cmd + " --verbose refresh")
      if subprocess.call(nimble_cmd + " --tarballs install cpython", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " --tarballs install cpython")
      else:
        print("ER\tFailed to run '" + nimble_cmd + " --tarballs install cpython'")
      if subprocess.call(nimble_cmd + " --tarballs install nodejs", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " --tarballs install nodejs")
      else:
        print("ER\tFailed to run '" + nimble_cmd + " --tarballs install nodejs'")
      if subprocess.call(nimble_cmd + " --tarballs install fusion", shell=True, timeout=999) == 0:
        print("OK\t" + nimble_cmd + " --tarballs install fusion")
      else:
        print("ER\tFailed to run '" + nimble_cmd + " --tarballs install fusion'")
    else:
      print("ER\tFailed to run '" + nimble_cmd + " refresh'")
  else:
    print("ER\tFile not found " + nimble_exe)
  return result


class X(install):

  def run(self):
    install.run(self)      # This is required by Python.
    if choosenim_setup():  # Check if choosenim is already installed.
      nim_setup()                   # Install Nim.
      if not sys.platform.startswith("win"):
        add_to_path(".bashrc")
        add_to_path(".profile")
        add_to_path(".bash_profile")
        add_to_path(".zshrc")
        add_to_path(".zshenv")
      else:  # Windows
        run_finishexe()
      if not nimble_setup():                       # Update Nimble.
        print("ER\tFailed to setup Nimble")
    else:
      raise Exception(IOError, "Failed to install Nim")

setuptools.setup(
  name         = "choosenim_install",
  author       = "Juan_Carlos.nim",
  cmdclass     = {"install": X},
  author_email = "UNKNOWN",
  url          = "UNKNOWN",
)
