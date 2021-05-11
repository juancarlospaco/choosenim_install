import os, sys, pathlib, warnings, setuptools, subprocess, shutil


assert sys.version_info > (3, 5, 0), "ERROR: Python version must be > 3.5!." # F-String.
os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
# shutil.rmtree(str(pathlib.Path.home() / ".choosenim"), ignore_errors=True)
# shutil.rmtree(str(pathlib.Path.home() / ".nimble"), ignore_errors=True)


class X(install):

  def nimble_setup(self):
    # After choosenim, we check that Nimble is working,
    # as "nimble" or "~/.nimble/bin/nimble", then install nimpy and fusion
    result = False
    ext = ".exe" if sys.platform.startswith("win") else ""
    nimble_exe = 'nimble' + ext  # Try "nimble"
    if subprocess.run(f"{ nimble_exe } --version", shell=True, check=True, timeout=99).returncode != 0:
      nimble_exe = pathlib.Path.home() / '.nimble' / 'bin' / 'nimble' + ext  # Try full path to "nimble"
      if subprocess.run(f"{ nimble_exe } --version", shell=True, check=True, timeout=99).returncode != 0:
        warnings.warn(f"Nimble not found, tried '{ nimble_exe }' and 'nimble'")
    # nim_exe = 'nimble' + ext  # Try "nim"
    # if subprocess.run(f"{ nim_exe } --version", shell=True, check=True, timeout=99).returncode != 0:
    #   nim_exe = pathlib.Path.home() / '.nimble' / 'bin' / 'nim' + ext  # Try full path to "nim"
    #   if subprocess.run(f"{ nim_exe } --version", shell=True, check=True, timeout=99).returncode != 0:
    #     warnings.warn(f"Nimble not found, tried '{ nim_exe }' and 'nim'")
    if os.exists(nimble_exe): # and os.exists(nim_exe):
      nimble_cmd = f"{ nimble_exe } --yes --verbose --noColor "   # --nim:'{nim_exe}'
      if subprocess.run(f"{ nimble_cmd } refresh", shell=True, check=True, timeout=999).returncode == 0:
        if subprocess.run(f"{ nimble_cmd } install nimpy", shell=True, check=True, timeout=999).returncode == 0:
          if subprocess.run(f"{ nimble_cmd } install fusion", shell=True, check=True, timeout=999).returncode == 0:
            result = True
          else:
            warnings.warn(f"Failed to run '{ nimble_cmd } install fusion'")
        else:
          warnings.warn(f"Failed to run '{ nimble_cmd } install nimpy'")
      else:
        warnings.warn(f"Failed to run '{ nimble_cmd } refresh'")
    else:
      warnings.warn(f"File not found '{ nimble_exe }'")
    return result

  def choosenim_setup(self):
    # Check for choosenim using "choosenim --version", to see if it is already installed,
    # if it is installed, run "choosenim update self" and "choosenim update stable",
    # if it is not installed run "init.sh" or "choosenim --firstInstall" to install choosenim.
    result = False
    choosenim_exe = "choosenim.exe" if sys.platform.startswith("win") else "choosenim"
    if subprocess.run(f"{ choosenim_exe } --version", shell=True, check=True, timeout=99).returncode == 0:
      warnings.warn(f"Choosenim is already installed and working on the system '{ choosenim_exe }'")
      if subprocess.run(f"{ choosenim_exe } update self", shell=True, check=True, timeout=999).returncode != 0:
        warnings.warn(f"Failed to run '{ choosenim_exe } update self'")  # Dont worry if "update self" fails.
      if subprocess.run(f"{ choosenim_exe } update stable", shell=True, check=True, timeout=999).returncode == 0:
        result = True
      else:
        warnings.warn(f"Failed to run '{ choosenim_exe } update stable'")
    else:
      choosenim_exe = pathlib.Path(__file__).parent / "choosenim.exe" if sys.platform.startswith("win") else "init.sh"
      if os.exists(choosenim_exe):
        choosenim_cmd = f"{ choosenim_exe } { ' --yes --verbose --noColor --firstInstall stable' if sys.platform.startswith('win') else ' -y' }"
        if subprocess.run(choosenim_cmd, shell=True, check=True, timeout=999).returncode == 0:
          result = True
        else:
          warnings.warn(f"Failed to run '{ choosenim_cmd }'")
      else:
        warnings.warn(f"File not found '{ choosenim_exe }'")
      shutil.rmtree(str(pathlib.Path.home() / ".choosenim" / "downloads"), ignore_errors=True)  # Clear download cache.
    return result

  def add_to_path(self):
    # On Linux add Nim to the PATH.
    if not sys.platform.startswith("win"):
      new_path = f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH"
      filename = pathlib.Path.home() / ".bashrc"
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
      except:
        warnings.warn(f"Failed to write file: {filename}")
      filename = pathlib.Path.home() / ".profile"
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
      except:
        warnings.warn("Failed to write file ~/.profile")
      filename = pathlib.Path.home() / ".bash_profile"
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
      except:
        warnings.warn("Failed to write file ~/.bash_profile")
      filename = pathlib.Path.home() / ".zshrc"
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
      except:
        warnings.warn("Failed to write file ~/.zshrc")

  def run(self):
    install.run(self)
    # TODO: nimble has a new "--noSSLCheck" that can be added in the future.
    if self.choosenim_setup():
      if self.nimble_setup():
        self.add_to_path()


setuptools.setup(cmdclass = {"install": X})
