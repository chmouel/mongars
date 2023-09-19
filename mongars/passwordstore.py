import subprocess


def get_item_from_pass(key: str) -> str:
    cmdline = f"pass show {key}"
    srun = subprocess.run(
        cmdline, stderr=subprocess.PIPE, shell=True, check=True, stdout=subprocess.PIPE
    )
    return srun.stdout.decode().strip()


def store_item_in_pass(key: str, content: str) -> None:
    cmdline = f"pass insert -f -m {key}"
    subprocess.run(
        cmdline, stderr=subprocess.PIPE, shell=True, check=True, input=content.encode()
    )
