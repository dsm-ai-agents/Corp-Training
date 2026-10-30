import subprocess, sys, pathlib
H = pathlib.Path(__file__).resolve().parent
for n in ['agent_1_data_clean.py','agent_2_summary.py']:
    if subprocess.run([sys.executable, H/n]).returncode: sys.exit(f'{n} failed')
ps = [subprocess.Popen([sys.executable, H/n]) for n in ['agent_3_powerpoint.py','agent_4_html.py']]
sys.exit(max(p.wait() for p in ps))
