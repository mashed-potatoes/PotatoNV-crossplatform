import sys
import chalk

if sys.version_info < (3, 6, 0):
    print(chalk.yellow("error"), "Python version is too old.")
    exit(1)
if __package__ != 'usrlock':
    print(chalk.yellow("Start Usrlock as package."))
    print(chalk.green("tip"), "python3.%d -m usrlock" % sys.version_info[1])
    exit(1)

from . import main
if __name__ == '__main__':
    main.main()