import sys
import contextlib
import shutil
import subprocess
from pathlib import Path


@contextlib.contextmanager
def backup():
    saved = []

    def save(path: Path):
        saved.append((path, path.parent / f"{path.name}.bck"))
        shutil.copyfile(*saved[-1])
        return saved[-1][0]

    try:
        yield save
    finally:
        for dst, src in saved:
            shutil.copyfile(src, dst)
            src.unlink()


def process():
    with backup() as save:
        readme = save(Path("README.rst"))
        print("massaging {readme} ..")
        txt = readme.read_text()
        readme.write_text(txt[txt.find(".. docs-index-start") :])

        print("creating wheel ..")
        subprocess.check_call([sys.executable, "-m", "build", "."])


if __name__ == "__main__":
    process()
