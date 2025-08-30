import subprocess
import os

DIRNAME = os.path.dirname(__file__)

def main():
    
    subprocess.run(['python', 'dataCleaning.py'], cwd=DIRNAME)
    
    subprocess.run(['python', 'DDM_2_2_2.py'], cwd=DIRNAME)

    subprocess.run(['python','plot.py'], cwd=DIRNAME)


if __name__ == '__main__':
    main()