import os, pathlib, warnings, setuptools, subprocess, shutil


os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
if sys.platform.startswith("win"):
  for dll_file in os.listdir(pathlib.Path(__file__).parent):
    if dll_file.endswith(".dll"):
      try:
        shutil.copyfile(dll_file, str( pathlib.Path(r"C:\Windows\System32") / pathlib.Path(dll_file).name ))
        subprocess.run(f"regsvr32 /s { pathlib.Path(r"C:\Windows\System32") / pathlib.Path(dll_file).name }", shell=True, check=False)
      except:
        print(f"Error: Failed to install DLL {dll_file}")
  if subprocess.run(f"{ pathlib.Path(__file__).parent / 'choosenim.exe' } --yes --verbose --noColor --firstInstall", shell=True, check=True, timeout=999).returncode == 0:
    subprocess.run('nimble.exe -y --noColor refresh'), shell=True, check=False, timeout=999)
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
