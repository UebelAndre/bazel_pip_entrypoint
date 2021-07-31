# bazel_pip_entrypoint

Rules for generating `py_binary` targets from wheel entry points

<a id="#py_pip_entrypoint"></a>

## py_pip_entrypoint

<pre>
py_pip_entrypoint(<a href="#py_pip_entrypoint-name">name</a>, <a href="#py_pip_entrypoint-wheel">wheel</a>, <a href="#py_pip_entrypoint-library">library</a>, <a href="#py_pip_entrypoint-entrypoint">entrypoint</a>, <a href="#py_pip_entrypoint-kwargs">kwargs</a>)
</pre>

Generate a py_bianry for an entry point or script from a wheel

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


**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="py_pip_entrypoint-name"></a>name |  The name given to the <code>py_binary</code>   |  none |
| <a id="py_pip_entrypoint-wheel"></a>wheel |  The label of a wheel   |  none |
| <a id="py_pip_entrypoint-library"></a>library |  The py_library target for the matching wheel   |  none |
| <a id="py_pip_entrypoint-entrypoint"></a>entrypoint |  An optinal name for the entry point or script. <code>name</code> is used if this is not set   |  <code>None</code> |
| <a id="py_pip_entrypoint-kwargs"></a>kwargs |  Additional keyword arguments for the underlying <code>py_binary</code>.   |  none |


