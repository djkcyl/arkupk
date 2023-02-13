import click

from pathlib import Path


@click.group(help="明日方舟解包工具")
@click.version_option(
    "0.1.0",
    "-v",
    "--version",
    package_name="arkupk",
    prog_name="ArkUPK",
    message="%(prog)s 当前版本：%(version)s",
    help="显示 ArkUPK 版本",
)
@click.help_option("-h", "--help", help="显示帮助信息")
def main():
    pass


@click.command(help="运行 ArkUPK")
@click.option("-A", "--all", is_flag=True, help="解包所有文件", default=False)
@click.option("-od", "--only-download", is_flag=True, help="仅下载文件", default=False)
@click.argument(
    "output",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    required=False,
    default="arkupk_output",
)
@click.help_option("-h", "--help", help="显示帮助信息")
def run(all: bool, only_download: bool, output: Path):
    output.mkdir(parents=True, exist_ok=True)

    from ..interface import run_tool

    run_tool(all, only_download, output)


main.add_command(run)
