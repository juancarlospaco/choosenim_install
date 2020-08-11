import os, pathlib, warnings, setuptools, subprocess, shutil


os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
if sys.platform.startswith("win"):
  shutil.rmtree(str(pathlib.Path.home() / ".choosenim"), ignore_errors=True)
  if subprocess.run(f"{ pathlib.Path(__file__).parent / 'choosenim.exe' } --yes --verbose --noColor --firstInstall stable", shell=True, check=True, timeout=9999).returncode == 0:
    subprocess.run("nimble.exe -y --noColor refresh", shell=True, check=False, timeout=999)
else:
  if subprocess.run(f"sh { pathlib.Path(__file__).parent / 'init.sh' } -y", shell=True, check=True, timeout=999).returncode == 0:
    if pathlib.Path(pathlib.Path.home() / ".nimble/bin").exists() and subprocess.run(str(pathlib.Path.home() / '.nimble/bin/nimble -y --noColor refresh'), shell=True, check=True, timeout=999).returncode == 0:
      new_path = f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH"
      try:
        found = False
        with open(pathlib.Path.home() / ".bashrc", "a") as f:
          for line in f:
            if new_path == line:
              found = True
          if not found:
            f.write(new_path)
      except:
        warnings.warn("Failed to write file ~/.bashrc")
      try:
        found = False
        with open(pathlib.Path.home() / ".profile", "a") as f:
          for line in f:
            if new_path == line:
              found = True
          if not found:
            f.write(new_path)
      except:
        warnings.warn("Failed to write file ~/.profile")
      try:
        found = False
        with open(pathlib.Path.home() / ".bash_profile", "a") as f:
          for line in f:
            if new_path == line:
              found = True
          if not found:
            f.write(new_path)
      except:
        warnings.warn("Failed to write file ~/.bash_profile")
      try:
        found = False
        with open(pathlib.Path.home() / ".zshrc", "a") as f:
          for line in f:
            if new_path == line:
              found = True
          if not found:
            f.write(new_path)
      except:
        warnings.warn("Failed to write file ~/.zshrc")


setuptools.setup()
