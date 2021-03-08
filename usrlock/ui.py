import chalk


def error(*data, critical=False):
    print(chalk.red("error"), " ".join(data))
    if critical:
        exit(1)


def success(*data):
    print(chalk.green("success"), " ".join(data))


def tip(*data):
    print(chalk.magenta("tip"), " ".join(data))


def info(*data):
    print(chalk.blue("info"), " ".join(data))


def progress(title=None, value=0, max_value=100):
    perc = int(100.0 * value / max_value)
    print(chalk.blue('%s%d%%' % (' ' * (3 - len(str(perc))), perc)), end='')
    if title:
        print(' %s' % title, end='')
    print(end='\r')
    if perc == 100:
        done()


def done():
    print(chalk.green('done'))
