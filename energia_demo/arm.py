"""ARM project DSL for offline demonstrations; unrelated to Arm CPU assembly.

Only the three documented declarations are accepted. No Python, shell, network
or hardware operations can be expressed. Owner strings are NOT authentication.
"""

import argparse
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re

from .model import DeviceGeneration, Simulation

MAX_CHARACTERS = 32768
MAX_LINES = 128
IDENTIFIER = r"[A-Za-z][A-Za-z0-9_]{0,63}"


class ArmError(ValueError):
    """A bounded syntax or simulation error with source-line context."""


@dataclass(frozen=True)
class Instruction:
    line: int
    operation: str
    arguments: tuple[str, ...]


def parse(source: str) -> tuple[Instruction, ...]:
    if not isinstance(source, str) or len(source) > MAX_CHARACTERS:
        raise ArmError("Source must be text of at most 32768 characters")
    lines = source.splitlines()
    if len(lines) > MAX_LINES:
        raise ArmError("Source exceeds the 128-line limit")
    instructions = []
    patterns = (
        ("OWNER", rf"OWNER\s+({IDENTIFIER})"),
        ("DEVICE", rf"DEVICE\s+({IDENTIFIER})\s+TYPE\s+([123])"),
        ("COMMAND", rf"COMMAND\s+({IDENTIFIER})\s+(activate|deactivate)"),
    )
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Optional terminal semicolon; multiple statements on one line are rejected.
        line = line.removesuffix(";").rstrip()
        for operation, pattern in patterns:
            match = re.fullmatch(pattern, line, flags=re.ASCII)
            if match:
                instructions.append(Instruction(number, operation, match.groups()))
                break
        else:
            raise ArmError(f"Line {number}: invalid ARM declaration")
    if not instructions or instructions[0].operation != "OWNER":
        raise ArmError("The first declaration must be OWNER")
    for instruction in instructions[1:]:
        if instruction.operation == "OWNER":
            raise ArmError(f"Line {instruction.line}: OWNER must occur exactly once")
    return tuple(instructions)


def run(source: str, *, actor: str, simulation: Simulation | None = None) -> Simulation:
    """Return a new simulated state; never mutate the supplied model, even on error.

    actor is supplied by the caller independently of the script. In production,
    that identity would have to originate from a separate authenticated session.
    """
    instructions = parse(source)
    owner = instructions[0].arguments[0]
    if actor not in Simulation.OWNERS or owner != actor:
        raise ArmError("OWNER must match the caller's known simulated identity")
    result = deepcopy(simulation) if simulation is not None else Simulation()
    for instruction in instructions[1:]:
        try:
            if instruction.operation == "DEVICE":
                device_id, generation = instruction.arguments
                result.register_device(actor, device_id, DeviceGeneration(f"type_{generation}"))
            else:
                device_id, command = instruction.arguments
                result.command_device(actor, device_id, "sleep" if command == "deactivate" else command)
        except (ValueError, PermissionError, KeyError) as exc:
            raise ArmError(f"Line {instruction.line}: simulation operation rejected ({exc})") from exc
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="UTF-8 ARM declaration file")
    parser.add_argument("--owner", choices=Simulation.OWNERS, required=True,
                        help="Simulated caller identity; not authentication")
    args = parser.parse_args(argv)
    try:
        with args.source.open(encoding="utf-8") as stream:
            source = stream.read(MAX_CHARACTERS + 1)
        demo = run(source, actor=args.owner)
    except (OSError, UnicodeError, ArmError) as exc:
        parser.exit(2, f"ARM demo error: {exc}\n")
    print(json.dumps({
        "mode": "OFFLINE SIMULATION — no hardware, authentication or real funds",
        "devices": [
            {"id": device.device_id, "owner": device.owner_id,
             "type": device.generation.value, "active": device.active}
            for device in demo.devices.values()
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
