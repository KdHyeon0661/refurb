from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, StrExpr

from refurb.checks.common import stringify
from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you want to open a Path object, don't pass it to `open()`, just call
    `.open()` on the Path object itself:

    Bad:

    ```
    path = Path("filename")

    with open(path) as f:
        pass
    ```

    Good:

    ```
    path = Path("filename")

    with path.open() as f:
        pass
    ```
    """

    name = "use-pathlib-open"
    code = 117
    categories = ("pathlib",)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.open") as open_node,
            args=[
                CallExpr(
                    callee=NameExpr(fullname="builtins.str"),
                    args=[arg],
                )
                | arg,
                *rest,
            ],
        ) if is_pathlike(arg):
            mode = args = ""

            match rest:
                case [StrExpr(value=value), *_]:
                    mode = f'"{value}"'
                    args = f", {mode}"

            inner = stringify(arg)
            expr = inner if arg == node.args[0] else f"str({inner})"

            msg = f"Replace `open({expr}{args})` with `{inner}.open({mode})`"

            errors.append(ErrorInfo.from_node(open_node, msg))
