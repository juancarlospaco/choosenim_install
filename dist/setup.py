import os, pathlib, warnings, setuptools, subprocess, shutil


os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
shutil.rmtree(str(pathlib.Path.home() / ".choosenim"), ignore_errors=True)
shutil.rmtree(str(pathlib.Path.home() / ".nimble"), ignore_errors=True)


if sys.platform.startswith("win"):
  if subprocess.run(f"{ pathlib.Path(__file__).parent / 'choosenim.exe' } --yes --verbose --noColor --firstInstall stable", shell=True, check=True, timeout=9999).returncode == 0:
    shutil.rmtree(str(pathlib.Path.home() / ".choosenim" / "downloads"), ignore_errors=True)
    subprocess.run(f"{ pathlib.Path.home() / '.nimble' / 'bin' / 'nimble.exe' } --yes --verbose --noColor refresh", shell=True, check=False, timeout=999)
else:
  if subprocess.run(f"sh { pathlib.Path(__file__).parent / 'init.sh' } -y", shell=True, check=True, timeout=999).returncode == 0:
    if pathlib.Path(pathlib.Path.home() / ".nimble/bin").exists() and subprocess.run(str(pathlib.Path.home() / '.nimble/bin/nimble -y --noColor refresh'), shell=True, check=True, timeout=999).returncode == 0:
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
        warnings.warn("Failed to write file: " + filename)
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


setuptools.setup()
