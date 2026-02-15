import subprocess, sys, os, time
args=[sys.executable,'planet3d.py','--planet','mars','--rotation','75','--out-file','static/from_web_mars_3.png','webuser','99','Earth']
kwargs={'cwd':os.getcwd(),'stdout':subprocess.DEVNULL,'stderr':subprocess.DEVNULL}
if os.name == 'nt':
    kwargs['creationflags'] = 0x08000000
p = subprocess.Popen(args, **kwargs)
print('started', p.pid)
# wait to allow process to finish
time.sleep(1)
print('exists?', os.path.exists('static/from_web_mars_3.png'))
