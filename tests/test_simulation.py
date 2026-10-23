import unittest
from decimal import Decimal
from fractions import Fraction

from energia_demo import DeviceGeneration, Simulation


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.demo = Simulation()

    def test_equal_immutable_ownership(self):
        self.assertEqual(sum(self.demo.shares.values()), 1)
        self.assertTrue(all(share == Fraction(1, 4) for share in self.demo.shares.values()))
        with self.assertRaises(TypeError):
            self.demo.shares["owner_a"] = Fraction(1)

    def test_all_generations_and_commands(self):
        for generation in DeviceGeneration:
            self.demo.register_device("owner_a", generation.value, generation)
            self.demo.command_device("owner_a", generation.value, "activate")
            self.assertTrue(self.demo.devices[generation.value].active)
            self.demo.command_device("owner_a", generation.value, "sleep")
            self.assertFalse(self.demo.devices[generation.value].active)

    def test_cross_owner_command_cannot_mutate_state(self):
        self.demo.register_device("owner_a", "coil", DeviceGeneration.TYPE_3)
        with self.assertRaises(PermissionError):
            self.demo.command_device("owner_b", "coil", "activate")
        self.assertFalse(self.demo.devices["coil"].active)

    def test_device_ownership_cannot_be_reassigned(self):
        self.demo.register_device("owner_a", "coil", DeviceGeneration.TYPE_1)
        with self.assertRaises(ValueError):
            self.demo.register_device("owner_b", "coil", DeviceGeneration.TYPE_2)
        self.assertEqual(self.demo.devices["coil"].owner_id, "owner_a")

    def test_unknown_owner_rejected(self):
        for operation in (
            lambda: self.demo.meditate("outsider", 20),
            lambda: self.demo.exchange_demo("outsider", "1"),
            lambda: self.demo.register_device("outsider", "coil", DeviceGeneration.TYPE_1),
        ):
            with self.assertRaises(PermissionError):
                operation()
        self.assertEqual(self.demo.issued_credits, 0)

    def test_accounting_and_isolation_after_fractional_exchanges(self):
        for owner in self.demo.OWNERS:
            self.demo.meditate(owner, 20)
            for _ in range(10):
                self.demo.exchange_demo(owner, "0.1")
                self.assertTrue(self.demo.accounting_is_balanced())
        self.assertEqual(self.demo.issued_credits, 80)
        self.assertEqual(self.demo.redeemed_credits, 4)
        self.assertEqual(self.demo.balances["owner_a"], Decimal("19"))
        self.demo.exchange_demo("owner_a", "19")
        self.assertEqual(self.demo.balances["owner_b"], Decimal("19"))
        self.assertEqual(self.demo.balances["owner_a"], 0)
        self.assertTrue(self.demo.accounting_is_balanced())

    def test_invalid_amounts_are_atomic(self):
        self.demo.meditate("owner_a", 5)
        before = (self.demo.balances, self.demo.demo_eth_balances, self.demo.ledger)
        for amount in ("0", "-1", "NaN", "Infinity", "bad", True, 0.1, "6", "1e30", "0.000000001"):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.demo.exchange_demo("owner_a", amount)
            self.assertEqual(before, (self.demo.balances, self.demo.demo_eth_balances, self.demo.ledger))
        self.assertTrue(self.demo.accounting_is_balanced())

    def test_invalid_meditation_durations(self):
        for minutes in (0, -1, 121, True, "20", 1.5):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                self.demo.meditate("owner_a", minutes)
        self.assertEqual(self.demo.ledger, ())

    def test_public_balances_are_read_only_snapshots(self):
        snapshot = self.demo.balances
        with self.assertRaises(TypeError):
            snapshot["owner_a"] = Decimal("999")
        self.demo.meditate("owner_a", 1)
        self.assertEqual(snapshot["owner_a"], 0)

    def test_sequence_and_determinism(self):
        other = Simulation()
        for model in (self.demo, other):
            model.meditate("owner_a", 20)
            model.exchange_demo("owner_a", "5")
        self.assertEqual(self.demo.ledger, other.ledger)
        self.assertEqual([entry.sequence for entry in self.demo.ledger], [1, 2])


if __name__ == "__main__":
    unittest.main()
