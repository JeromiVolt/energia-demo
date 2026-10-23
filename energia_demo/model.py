"""Deterministic accounting model for a fictional product demonstration.

Caller-provided owner IDs are a simulation boundary, NOT authentication.
This module does not implement quantum computing, energy transfer, biometrics,
medical effects, blockchain transactions, or investment returns.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from fractions import Fraction
from types import MappingProxyType


class DeviceGeneration(str, Enum):
    TYPE_1 = "type_1"
    TYPE_2 = "type_2"
    TYPE_3 = "type_3"


@dataclass(frozen=True)
class Device:
    device_id: str
    owner_id: str
    generation: DeviceGeneration
    active: bool = False


@dataclass(frozen=True)
class LedgerEntry:
    sequence: int
    operation: str
    owner_id: str
    credits: Decimal
    demo_eth: Decimal = Decimal("0")


def positive_amount(value: str | int | Decimal) -> Decimal:
    """Require exact decimal input; reject floats, booleans, NaN and infinity."""
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("Use a decimal string, integer or Decimal")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal amount") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be finite and positive")
    # Bound precision so ordinary Decimal context cannot silently round balances.
    if amount > Decimal("1000000000") or amount.as_tuple().exponent < -8:
        raise ValueError("Demo amounts support at most 1 billion and 8 decimal places")
    return amount


class Simulation:
    """Four equal owners, isolated device control, and strictly simulated credits."""

    OWNERS = ("owner_a", "owner_b", "owner_c", "owner_d")
    MEDITATION_CREDITS_PER_MINUTE = Decimal("1")
    # An arbitrary illustration, not a market price or redeemable exchange rate.
    DEMO_ETH_PER_CREDIT = Decimal("0.001")

    def __init__(self):
        self._balances = {owner: Decimal("0") for owner in self.OWNERS}
        self._demo_eth = {owner: Decimal("0") for owner in self.OWNERS}
        self._devices: dict[str, Device] = {}
        self._ledger: list[LedgerEntry] = []
        self._issued = Decimal("0")
        self._redeemed = Decimal("0")

    @property
    def shares(self):
        return MappingProxyType({owner: Fraction(1, 4) for owner in self.OWNERS})

    @property
    def balances(self):
        return MappingProxyType(dict(self._balances))

    @property
    def demo_eth_balances(self):
        return MappingProxyType(dict(self._demo_eth))

    @property
    def devices(self):
        return MappingProxyType(dict(self._devices))

    @property
    def ledger(self):
        return tuple(self._ledger)

    @property
    def issued_credits(self):
        return self._issued

    @property
    def redeemed_credits(self):
        return self._redeemed

    def _owner(self, actor: str):
        if actor not in self.OWNERS:
            raise PermissionError("Unknown simulated owner")

    def register_device(self, actor: str, device_id: str, generation: DeviceGeneration):
        self._owner(actor)
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("Device ID must be nonempty")
        if device_id in self._devices:
            raise ValueError("Device already registered; ownership cannot be reassigned")
        if not isinstance(generation, DeviceGeneration):
            raise ValueError("Use a DeviceGeneration enum value")
        self._devices[device_id] = Device(device_id, actor, generation)

    def command_device(self, actor: str, device_id: str, command: str):
        self._owner(actor)
        device = self._devices[device_id]
        if device.owner_id != actor:
            raise PermissionError("A simulated owner controls only their own device")
        if command not in ("activate", "sleep"):
            raise ValueError("Supported demo commands: activate, sleep")
        self._devices[device_id] = Device(
            device.device_id, device.owner_id, device.generation, command == "activate"
        )

    def meditate(self, actor: str, minutes: int):
        """Record a fictional session; no sensing or health inference occurs."""
        self._owner(actor)
        if isinstance(minutes, bool) or not isinstance(minutes, int) or not 1 <= minutes <= 120:
            raise ValueError("Demo duration must be an integer from 1 to 120 minutes")
        credits = minutes * self.MEDITATION_CREDITS_PER_MINUTE
        self._balances[actor] += credits
        self._issued += credits
        self._record("simulated_meditation", actor, credits)
        return credits

    def exchange_demo(self, actor: str, credits: str | int | Decimal):
        """Move credits into the redeemed pool and mint nonredeemable demo ETH."""
        self._owner(actor)
        amount = positive_amount(credits)
        if amount > self._balances[actor]:
            raise ValueError("Insufficient simulated credits")
        demo_eth = amount * self.DEMO_ETH_PER_CREDIT
        self._balances[actor] -= amount
        self._redeemed += amount
        self._demo_eth[actor] += demo_eth
        self._record("simulated_exchange", actor, amount, demo_eth)
        return demo_eth

    def _record(self, operation, actor, credits, demo_eth=Decimal("0")):
        self._ledger.append(LedgerEntry(len(self._ledger) + 1, operation, actor, credits, demo_eth))

    def accounting_is_balanced(self):
        return (
            sum(self._balances.values(), Decimal("0")) + self._redeemed == self._issued
            and sum(self._demo_eth.values(), Decimal("0"))
            == self._redeemed * self.DEMO_ETH_PER_CREDIT
            and all(value >= 0 for value in self._balances.values())
        )
