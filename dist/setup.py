import os, pathlib, setuptools, subprocess

os.environ["CHOOSENIM_NO_ANALYTICS"] = "1"
if subprocess.run(f"sh { pathlib.Path(__file__).parent / 'init.sh' } -y", shell=True, check=True).returncode == 0:
  if subprocess.run(str(pathlib.Path.home() / '.nimble/bin/nimble -y --noColor refresh'), shell=True, check=True).returncode == 0:
    try:
      with open(pathlib.Path.home() / ".bashrc", "a") as f:
        f.write(f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH")
    except:
      pass
    try:
      with open(pathlib.Path.home() / ".profile", "a") as f:
        f.write(f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH")
    except:
      pass
    try:
      with open(pathlib.Path.home() / ".bash_profile", "a") as f:
        f.write(f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH")
    except:
      pass
    try:
      with open(pathlib.Path.home() / ".zshrc", "a") as f:
        f.write(f"export PATH={ pathlib.Path.home() / '.nimble/bin' }:$PATH")
    except:
      pass

setuptools.setup()
