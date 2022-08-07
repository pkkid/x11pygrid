__ONLY__ for development testing purposes.

- VirtualBox doesn't handle complex keys combinations well, it's going to uhid keyboard.
  You can verify that with ```xev```. Because of that, it's good idea to modify x11pygrid.json configuration file.
  Simply replace ```"accelerator" : "<Ctrl><Mod1><Mod2>"``` with ```"accelerator" : "<Ctrl>"```. Since you make that,
  all old keys combinations do NOT need ```<Alt>``` key.
  So: ```<Ctrl> + <Num_1>```, ```<Ctrl> + <Num_2>``` etc.
  It works with Ubuntu. With FreeBSD doesn't and I've no idea why... but for pipx installation tests etc. it was enough.
  If you've any idea how to pass hotkeys to VM with FreeBSD, feel free to help! Thanks in advance!
- Don't you know FreeBSD? Take it easy, just login and ```startx``` to run X. Looks familiar? It should!