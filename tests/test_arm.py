import unittest

from energia_demo import DeviceGeneration, Simulation
from energia_demo.arm import ArmError, parse, run


class ArmTests(unittest.TestCase):
    def test_valid_program_all_types_and_deactivation(self):
        model = run("""# Offline declarations
OWNER owner_a;
DEVICE coil_a TYPE 1;
DEVICE coil_b TYPE 2
DEVICE coil_c TYPE 3
COMMAND coil_a activate
COMMAND coil_b activate;
COMMAND coil_b deactivate;
""", actor="owner_a")
        self.assertTrue(model.devices["coil_a"].active)
        self.assertFalse(model.devices["coil_b"].active)
        self.assertEqual(model.devices["coil_c"].generation, DeviceGeneration.TYPE_3)

    def test_owner_cannot_be_impersonated(self):
        for actor in ("owner_b", "unknown"):
            with self.subTest(actor=actor), self.assertRaises(ArmError):
                run("OWNER owner_a", actor=actor)

    def test_foreign_device_cannot_be_commanded(self):
        initial = Simulation()
        initial.register_device("owner_b", "foreign", DeviceGeneration.TYPE_3)
        with self.assertRaises(ArmError):
            run("OWNER owner_a\nCOMMAND foreign activate", actor="owner_a", simulation=initial)
        self.assertFalse(initial.devices["foreign"].active)

    def test_invalid_program_does_not_partially_mutate_input(self):
        initial = Simulation()
        with self.assertRaises(ArmError):
            run("OWNER owner_a\nDEVICE coil TYPE 1\nCOMMAND absent activate",
                actor="owner_a", simulation=initial)
        self.assertEqual(dict(initial.devices), {})

    def test_success_returns_independent_state(self):
        initial = Simulation()
        result = run("OWNER owner_a\nDEVICE coil TYPE 1", actor="owner_a", simulation=initial)
        self.assertIn("coil", result.devices)
        self.assertEqual(dict(initial.devices), {})

    def test_only_finite_documented_grammar(self):
        invalid_sources = (
            "", "COMMAND coil activate", "OWNER owner_a\nOWNER owner_b",
            "OWNER owner_a\nDEVICE coil TYPE 4", "OWNER owner_a; COMMAND coil activate",
            "OWNER owner_a\nCOMMAND coil sleep", "OWNER owner_a\nimport os",
            "OWNER owner_a\n__import__('os').system('echo should_not_run')",
            "OWNER owner_a\nWHILE true", "OWNER owner_a\nDEVICE coil; TYPE 1",
            "OWNER owner_a\n" + "# comment\n" * 128,
            "OWNER owner_a\n#" + "x" * 32768,
        )
        for source in invalid_sources:
            with self.subTest(source=source[:80]), self.assertRaises(ArmError):
                parse(source)

    def test_error_includes_line_number(self):
        with self.assertRaisesRegex(ArmError, "Line 3"):
            parse("OWNER owner_a\n# comment\nINVALID")


if __name__ == "__main__":
    unittest.main()
