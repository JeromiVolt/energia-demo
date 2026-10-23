"""Run with python3 -m energia_demo from the repository root."""

import json

from .model import DeviceGeneration, Simulation


def main():
    demo = Simulation()
    for owner in demo.OWNERS:
        for generation in DeviceGeneration:
            demo.register_device(owner, f"{owner}_{generation.value}", generation)
    demo.command_device("owner_a", "owner_a_type_3", "activate")
    demo.meditate("owner_a", 20)
    demo.exchange_demo("owner_a", "5")
    print(json.dumps({
        "mode": "OFFLINE SIMULATION — no real funds, hardware, authentication or medical effects",
        "shares": {owner: str(share) for owner, share in demo.shares.items()},
        "simulated_credits": {owner: str(value) for owner, value in demo.balances.items()},
        "nonredeemable_demo_eth": {owner: str(value) for owner, value in demo.demo_eth_balances.items()},
        "accounting_balanced": demo.accounting_is_balanced(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
