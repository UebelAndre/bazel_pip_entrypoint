"""Rules for generating `py_binary` targets from wheel entry points"""

load("@rules_python//python:defs.bzl", "py_binary")

def _py_pip_entrypoint_impl(ctx):
    entrypoint = ctx.attr.entrypoint
    entrypoint_file = ctx.actions.declare_file(ctx.label.name)
    optional_script_file = ctx.actions.declare_file("{}.script/{}".format(
        ctx.label.name,
        entrypoint,
    ))

    args = ctx.actions.args()
    args.add("--entrypoint", entrypoint)
    args.add("--wheel", ctx.file.wheel.path)
    args.add("--output", entrypoint_file.path)
    args.add("--out_script_path", optional_script_file.path)
    args.add("--out_script_short_path", optional_script_file.short_path)

    ctx.actions.run(
        arguments = [args],
        outputs = [entrypoint_file, optional_script_file],
        executable = ctx.executable._script,
        mnemonic = "PyPipEntrypoint",
        progress_message = "Extracting entrypoint '{}' from wheel '{}'".format(
            entrypoint,
            ctx.attr.wheel.label,
        ),
        inputs = [ctx.file.wheel],
    )

    return [
        DefaultInfo(
            files = depset([entrypoint_file]),
        ),
        OutputGroupInfo(
            script = depset([optional_script_file]),
        ),
    ]

_py_pip_entrypoint = rule(
    doc = "A rule for generating an entrypoint from a python wheel",
    implementation = _py_pip_entrypoint_impl,
    attrs = {
        "entrypoint": attr.string(
            doc = "The name of the entry point or script",
            mandatory = True,
        ),
        "wheel": attr.label(
            doc = "The wheel containing the entrypoint",
            allow_single_file = True,
            mandatory = True,
        ),
        "_script": attr.label(
            doc = "A script for extracting an entry point from a wheel",
            executable = True,
            cfg = "exec",
            default = Label("//private:entrypoint_script_maker"),
        ),
    },
)

def py_pip_entrypoint(name, wheel, library, entrypoint = None, **kwargs):
    """Generate a py_bianry for an entry point or script from a wheel

    An example of this macro generating a `pip` `py_binary` target can be seen below:
    ```python
    load("@pip.python_test//:requirements.bzl", "requirement", "whl_requirement")
    load("@bazel_pip_entrypoint//:python.bzl", "py_pip_entrypoint")

    # Uses entry_points.txt
    py_pip_entrypoint(
        name = "pip",
        library = requirement("pip"),
        wheel = whl_requirement("pip"),
    )
    ```

    Args:
        name (str): The name given to the `py_binary`
        wheel (Label): The label of a wheel
        library (Label): The py_library target for the matching wheel
        entrypoint (str, optional): An optinal name for the entry point or script.
            `name` is used if this is not set
        **kwargs (dict): Additional keyword arguments for the underlying `py_binary`.
    """
    entrypoint_name = "{}_pip_entry_point.py".format(name)

    _py_pip_entrypoint(
        name = entrypoint_name,
        wheel = wheel,
        tags = ["manual"],
        entrypoint = entrypoint or name,
    )

    script_name = "{}_pip_script".format(name)
    native.filegroup(
        name = script_name,
        srcs = [entrypoint_name],
        output_group = "script",
    )

    py_binary(
        name = name,
        srcs = [entrypoint_name],
        main = entrypoint_name,
        deps = [library],
        data = [script_name],
        **kwargs
    )
