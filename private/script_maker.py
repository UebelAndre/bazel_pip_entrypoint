#!/usr/bin/env python3

from pathlib import Path
from typing import Optional
import argparse
import configparser
import tempfile
import zipfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("script_maker")

    parser.add_argument(
        "--wheel", type=Path, required=True, help="The wheel of a package that contains entrypoint scripts",
    )
    parser.add_argument(
        "--entrypoint", type=str, required=True, help="The entrypoint to search for",
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="The path of the output file to generate",
    )
    parser.add_argument(
        "--out_script_path", type=Path, required=True, help="A path to an optionally generated script",
    )
    parser.add_argument(
        "--out_script_short_path", type=Path, required=True, help="A path to an optionally generated script",
    )

    return parser.parse_args()


def get_wheel_name(wheel: Path) -> str:
    name, version, _ = wheel.name.split("-", 2)
    return "{}-{}".format(name, version)


def extract_wheel(wheel_name: str, wheel: Path, out_dir: Path) -> None:
    data_dir = "{}.data".format(wheel_name)
    dist_info = "{}.dist-info".format(wheel_name)
    with zipfile.ZipFile(wheel, 'r') as zip:
        for member in zip.filelist:
            filename = member.filename
            # Only extract dist-info and data
            if filename.startswith(data_dir) or filename.startswith(dist_info):
                zip.extract(member, out_dir)


def find_entrypoints_file(wheel_name: str, wheel_dir: Path) -> Optional[Path]:
    entry_points_file = wheel_dir / "{}.dist-info".format(wheel_name) / "entry_points.txt"
    if entry_points_file.exists():
        return entry_points_file
    return None


ENTRY_POINT_TEMPLATE = """\
#!/usr/bin/env python
if __name__ == "__main__":
    from {module} import {method}
    {method}()
"""


def generate_entrypoint(entrypoints_txt: Path, entrypoint: str, output: Path) -> None:
    # First check for an entrypoints file
    config = configparser.ConfigParser()
    config.read(entrypoints_txt)
    option = config.get("console_scripts", entrypoint)
    if option:
        module, method = option.split(":", 1)
        output.write_text(ENTRY_POINT_TEMPLATE.format(
            module=module,
            method=method
        ))


def find_scripts_dir(wheel_name: str, wheel_dir: Path) -> Optional[Path]:
    scripts_dir = wheel_dir / "{}.data".format(wheel_name) / "scripts"
    if scripts_dir.exists():
        return scripts_dir
    return None


SCRIPT_TEMPLATE = """\
#!/usr/bin/env python
if __name__ == "__main__":
    import os
    import sys
    script_path = "{script_path}"
    args = sys.argv.copy()
    args[0] = script_path
    os.execv(sys.executable, [sys.executable] + args)
"""


def generate_script(
        scripts_dir: Path,
        script_name: str,
        output: Path,
        out_script_path: Path,
        out_script_short_path: Path) -> None:
    for file in scripts_dir.iterdir():
        if file.name == script_name:
            output.write_text(SCRIPT_TEMPLATE.format(
                script_path=str(out_script_short_path)
            ))
            file.replace(out_script_path)
            break


def main() -> None:
    options = parse_args()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        wheel_name = get_wheel_name(options.wheel)

        # Extract the wheel
        extract_wheel(
            wheel_name=wheel_name,
            wheel=options.wheel,
            out_dir=temp_dir_path,
        )

        # Attempt to find the entry_point.txt file
        entrypoints_txt = find_entrypoints_file(
            wheel_name=wheel_name,
            wheel_dir=temp_dir_path,
        )

        # Generate the entrypoint file from the extracted wheel
        if entrypoints_txt:
            generate_entrypoint(
                entrypoints_txt=entrypoints_txt,
                entrypoint=options.entrypoint,
                output=options.output,
            )

            # Entrypoints have no scripts so we write an empty file for
            # the output script
            options.out_script_path.write_text("")

            return

        # Some wheels have a `*.data/scripts` directory contianing scripts.
        scripts_dir = find_scripts_dir(
            wheel_name=wheel_name,
            wheel_dir=temp_dir_path,
        )

        
        # generate the script if available
        if scripts_dir:
            generate_script(
                scripts_dir=scripts_dir,
                script_name=options.entrypoint,
                output=options.output,
                out_script_path=options.out_script_path,
                out_script_short_path=options.out_script_short_path,
            )

            return

        raise RuntimeError("The current wheel has no entry points or scripts", wheel_name)


if __name__ == "__main__":
    main()
