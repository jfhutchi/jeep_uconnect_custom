import unittest

from analysis_tools.arm_elf_analysis import Elf32Image
from analysis_tools.tests.test_arm_elf_analysis import _elf32
from analysis_tools.synctool_evidence import Anchor, check_anchor, verify_image


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.image = Elf32Image.from_bytes(_elf32(bytes.fromhex("240090e5") + b"name\0"))

    def test_word_instruction_and_string_anchors(self) -> None:
        checks = (
            Anchor("field load", 0x1000, "instruction", "ldr r0, [r0, #0x24]"),
            Anchor("test word", 0x1000, "word", "0xE5900024"),
            Anchor("test string", 0x1004, "string", "name"),
        )
        for anchor in checks:
            self.assertTrue(check_anchor(self.image, anchor).passed)

    def test_mismatch_and_unmapped_anchor_do_not_pass(self) -> None:
        for address in (0x1000, 0x2000):
            result = check_anchor(self.image, Anchor("bad", address, "word", "0"))
            self.assertFalse(result.passed)

    def test_refuses_unrecognized_vendor_image_hash(self) -> None:
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            verify_image(self.image)

    def test_unknown_anchor_type_is_an_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "kind"):
            check_anchor(self.image, Anchor("bad", 0x1000, "unknown", ""))


if __name__ == "__main__":
    unittest.main()
