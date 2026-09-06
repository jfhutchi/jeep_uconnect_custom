import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from analysis_tools.qnx_media_runtime_probe import _scan_stream, build_report, scan_root


class StreamTests(unittest.TestCase):
    def test_marker_crossing_chunk_boundary_is_counted_once(self):
        data = b"xxxxlibcodecengine.so and H264"
        digest, matches, consumed = _scan_stream(
            io.BytesIO(data), chunk_bytes=7, max_offsets=4
        )
        self.assertEqual(consumed, len(data))
        self.assertEqual(digest, hashlib.sha256(data).hexdigest())
        self.assertEqual(matches["libcodecengine"]["count"], 1)
        self.assertEqual(matches["libcodecengine"]["offsets"], [4])
        self.assertEqual(matches["h264"]["count"], 1)

    def test_qnx_and_harman_integration_markers_are_case_insensitive(self):
        data = (
            b"X/pps/services/launcher/control HMI-Notification "
            b"screen_create_window_group PhoneProjectionService ModuleLink "
            b"event-source-handsfree HFP_CALL_INCOMING "
            b"/pps/services/bluetooth/handsfree/status bar-descriptor.xml "
            b'<asset type="Qnx/Elf" entry="true"> run_native '
            b"audio_manager_get_handle /pps/services/audio/audio_router_control "
            b"/pps/services/audio/audio_router_status /pps/services/audio/control "
            b"/pps/services/audio/devices/speaker /pps/services/audio/status "
            b"/pps/services/audio/types/voice /pps/services/audio/voice_status "
            b"/pps/services/multimedia/mediacontroller/control "
            b"/pps/services/multimedia/mediaplayer/control "
            b"/pps/services/multimedia/mediaplayer/phone "
            b"/pps/services/multimedia/mediaplayer/status io-audio io-acoustic pps-bluetooth "
            b"audioMgrCMC.conf AudioCtrlSvc audioApp "
            b"screen_join_window_group SCREEN_PROPERTY_FOCUS "
            b"SCREEN_PROPERTY_SENSITIVITY SCREEN_EVENT_MTOUCH_TOUCH video_hmi "
            b"boot.sh graphics.conf ModuleLink.xml processStarter "
            b"DeviceProjection.swf PROJECTION_BACKTO_CAR PhoneProjectionEvent "
            b"com.aicas.xlet.manager.AMS com.harman.service.AppManager "
            b"AppManager_JavaApps /fs/mmc1/xletsdir xlet.properties "
            b"usblauncher io-usb-dcd RoleSwap_DigitaliPodOut "
            b"RoleSwap_AppleDevice iAP2 mm-ipod io-fs-media itun libipod "
            b"devu-dcd-omap3.so devu-usbumass-omap3.so "
            b"devu-usbser-omap3.so devu-usbncm-omap3.so "
            b"devu-usbrndis-omap3.so libusbdci.so Device_Stack "
            b"/pps/qnx/device/usb_ctrl start_stack::device ulink_ctrl "
            b"omap3530-mg ehci-omap3 pmic_tw4030_cfg 0x480ab000"
        )
        _, matches, _ = _scan_stream(
            io.BytesIO(data), chunk_bytes=11, max_offsets=4
        )
        self.assertEqual(matches["pps_launcher"]["count"], 1)
        self.assertEqual(
            matches["pps_launcher"]["offsets"],
            [data.lower().index(b"/pps/services/launcher")],
        )
        self.assertEqual(matches["hmi_notification"]["count"], 1)
        self.assertEqual(matches["screen_window_group"]["count"], 1)
        self.assertEqual(matches["phone_projection_service"]["count"], 1)
        self.assertEqual(matches["modulelink"]["count"], 1)
        self.assertEqual(matches["hnm_handsfree_plugin"]["count"], 1)
        self.assertEqual(matches["hnm_hfp_call_incoming"]["count"], 1)
        self.assertEqual(matches["pps_bluetooth_handsfree"]["count"], 1)
        self.assertEqual(matches["bar_descriptor"]["count"], 1)
        self.assertEqual(matches["qnx_elf_asset"]["count"], 1)
        self.assertEqual(matches["run_native"]["count"], 1)
        self.assertEqual(matches["audio_manager"]["count"], 1)
        self.assertEqual(matches["audio_manager_get_handle"]["count"], 1)
        self.assertEqual(matches["audio_mgr_cmc_config"]["count"], 1)
        self.assertEqual(matches["audio_ctrl_svc"]["count"], 1)
        self.assertEqual(matches["audio_app_source"]["count"], 1)
        self.assertEqual(matches["screen_join_window_group"]["count"], 1)
        self.assertEqual(matches["screen_property_focus"]["count"], 1)
        self.assertEqual(matches["screen_property_sensitivity"]["count"], 1)
        self.assertEqual(matches["screen_event_mtouch"]["count"], 1)
        self.assertEqual(matches["video_hmi_class"]["count"], 1)
        self.assertEqual(matches["boot_script"]["count"], 1)
        self.assertEqual(matches["graphics_config"]["count"], 1)
        self.assertEqual(matches["modulelink_config"]["count"], 1)
        self.assertEqual(matches["process_starter"]["count"], 1)
        self.assertEqual(matches["device_projection_swf"]["count"], 1)
        self.assertEqual(matches["projection_back_to_car"]["count"], 1)
        self.assertEqual(matches["phone_projection_event"]["count"], 1)
        self.assertEqual(matches["ams_service"]["count"], 1)
        self.assertEqual(matches["app_manager_service"]["count"], 1)
        self.assertEqual(matches["appmanager_javaapps"]["count"], 1)
        self.assertEqual(matches["xlets_directory"]["count"], 1)
        self.assertEqual(matches["xlet_properties"]["count"], 1)
        self.assertEqual(matches["usblauncher"]["count"], 1)
        self.assertEqual(matches["io_usb_dcd"]["count"], 1)
        self.assertEqual(matches["roleswap_digitalipodout"]["count"], 1)
        self.assertEqual(matches["roleswap_appledevice"]["count"], 1)
        self.assertEqual(matches["iap2"]["count"], 1)
        self.assertEqual(matches["mm_ipod"]["count"], 1)
        self.assertEqual(matches["io_fs_media"]["count"], 1)
        self.assertEqual(matches["itun"]["count"], 1)
        self.assertEqual(matches["libipod"]["count"], 1)
        self.assertEqual(matches["devu_dcd"]["count"], 1)
        self.assertEqual(matches["devu_usbumass_hw"]["count"], 1)
        self.assertEqual(matches["devu_usbser_hw"]["count"], 1)
        self.assertEqual(matches["devu_usbncm_hw"]["count"], 1)
        self.assertEqual(matches["devu_usbrndis_hw"]["count"], 1)
        self.assertEqual(matches["libusbdci"]["count"], 1)
        self.assertEqual(matches["usb_device_stack_rule"]["count"], 1)
        self.assertEqual(matches["usb_ctrl_pps"]["count"], 1)
        self.assertEqual(matches["start_stack_device"]["count"], 1)
        self.assertEqual(matches["ulink_ctrl"]["count"], 1)
        self.assertEqual(matches["omap3530_mg"]["count"], 1)
        self.assertEqual(matches["ehci_omap3"]["count"], 1)
        self.assertEqual(matches["pmic_tw4030_cfg"]["count"], 1)
        self.assertEqual(matches["omap_otg_base"]["count"], 1)
        self.assertEqual(matches["pps_audio_control"]["count"], 1)
        self.assertEqual(matches["pps_audio_router_control"]["count"], 1)
        self.assertEqual(matches["pps_audio_router_status"]["count"], 1)
        self.assertEqual(matches["pps_audio_devices"]["count"], 1)
        self.assertEqual(matches["pps_audio_status"]["count"], 1)
        self.assertEqual(matches["pps_audio_types"]["count"], 1)
        self.assertEqual(matches["pps_audio_voice_status"]["count"], 1)
        self.assertEqual(matches["pps_mediacontroller_control"]["count"], 1)
        self.assertEqual(matches["pps_mediaplayer_control"]["count"], 1)
        self.assertEqual(matches["pps_mediaplayer_phone"]["count"], 1)
        self.assertEqual(matches["pps_mediaplayer_status"]["count"], 1)
        self.assertEqual(matches["io_audio"]["count"], 1)
        self.assertEqual(matches["io_acoustic"]["count"], 1)
        self.assertEqual(matches["pps_bluetooth"]["count"], 1)

    def test_offset_cap_preserves_full_count(self):
        data = b"h264--h264--h264"
        _, matches, _ = _scan_stream(io.BytesIO(data), chunk_bytes=5, max_offsets=1)
        self.assertEqual(matches["h264"]["count"], 3)
        self.assertEqual(matches["h264"]["offsets"], [0])
        self.assertTrue(matches["h264"]["offsets_truncated"])

    def test_invalid_scan_limits_fail(self):
        with self.assertRaises(ValueError):
            _scan_stream(io.BytesIO(b"x"), chunk_bytes=0)
        with self.assertRaises(ValueError):
            _scan_stream(io.BytesIO(b"x"), max_offsets=-1)


class RootTests(unittest.TestCase):
    def test_reports_relative_paths_hashes_and_controlled_markers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "hidden_hbc"
            target = root / "usr" / "lib" / "libcodecengine.so.1"
            target.parent.mkdir(parents=True)
            payload = b"prefix decodeCombo middle screen_create_window_buffers suffix"
            target.write_bytes(payload)
            (root / "ordinary.bin").write_bytes(b"private unrelated bytes")

            report = scan_root(root, chunk_bytes=9)
            self.assertEqual(report["root_label"], "hidden_hbc")
            self.assertEqual(report["files_scanned"], 2)
            self.assertEqual(len(report["findings"]), 1)
            finding = report["findings"][0]
            self.assertEqual(finding["path"], "usr/lib/libcodecengine.so.1")
            self.assertEqual(finding["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertIn("libcodecengine", finding["filename_tags"])
            self.assertEqual(
                finding["content_markers"]["decodecombo"]["offsets"],
                [payload.lower().index(b"decodecombo")],
            )
            rendered = json.dumps(report)
            self.assertNotIn("private unrelated bytes", rendered)
            self.assertNotIn(str(root.resolve()), rendered)

    def test_oversized_file_is_explicitly_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            root.mkdir()
            (root / "h264_blob.bin").write_bytes(b"x" * 9)
            report = scan_root(root, max_file_bytes=8)
            self.assertEqual(report["files_scanned"], 0)
            self.assertEqual(report["files_skipped"], 1)
            self.assertEqual(report["skipped"][0]["path"], "h264_blob.bin")
            self.assertEqual(report["findings"], [])

    def test_build_report_totals_multiple_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            roots = [base / "one", base / "two"]
            for root in roots:
                root.mkdir()
            (roots[0] / "sgx530.conf").write_bytes(b"gpu")
            (roots[1] / "boot.sh").write_bytes(b"startup-omap3730")
            report = build_report(roots)
            self.assertEqual(report["format"], "qnx-media-runtime-evidence-v1")
            self.assertEqual(report["totals"]["roots"], 2)
            self.assertEqual(report["totals"]["files_scanned"], 2)
            self.assertEqual(report["totals"]["findings"], 2)


    def test_build_report_disambiguates_duplicate_root_basenames(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            roots = [base / "one" / "files", base / "two" / "files"]
            for root in roots:
                root.mkdir(parents=True)
                (root / "boot.sh").write_bytes(b"startup")
            report = build_report(roots)
            self.assertEqual(
                [root["root_label"] for root in report["roots"]],
                ["files#1", "files#2"],
            )


if __name__ == "__main__":
    unittest.main()
