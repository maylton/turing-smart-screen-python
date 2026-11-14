import unittest

from library.lcd.lcd_comm_rev_c import LcdCommRevC, Orientation, Count, SubRevision

from .serial_mock import new_testing_serial
from .sample_image import generate_sample_image


class MockedLcdCommRevC(LcdCommRevC):
    def openSerial(self):
        self.lcd_serial = new_testing_serial()

    def expect_golden(self, tc: unittest.TestCase, fn: str):
        self.lcd_serial.expect_golden(tc, fn)

sample_img_portrait = generate_sample_image(480, 800)
sample_img_landscape = generate_sample_image(800, 480)

class TestLcdCommRevC(unittest.TestCase):
    def test_set_brightness(self):
        lcd = MockedLcdCommRevC()
        lcd.SetBrightness()

        lcd.expect_golden(self, "rev_c_set_brightness")

    # display_pil_image_<orientation> : display a full-screen image

    def test_display_pil_image_portrait(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.PORTRAIT)
        lcd.DisplayPILImage(sample_img_portrait)

        lcd.expect_golden(self, "rev_c_display_pil_image_portrait")

    def test_display_pil_image_landscape(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.LANDSCAPE)
        lcd.DisplayPILImage(sample_img_landscape)

        lcd.expect_golden(self, "rev_c_display_pil_image_landscape")

    def test_display_pil_image_reverse_portrait(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.REVERSE_PORTRAIT)
        lcd.DisplayPILImage(sample_img_portrait)

        lcd.expect_golden(self, "rev_c_display_pil_image_reverse_portrait")

    def test_display_pil_image_reverse_landscape(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)
        lcd.DisplayPILImage(sample_img_landscape)

        lcd.expect_golden(self, "rev_c_display_pil_image_reverse_landscape")

    # display_pil_image_patch_<orientation> : display a less-than-full-screen image at a given location

    def test_display_pil_image_patch_portrait(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.PORTRAIT)
        lcd.DisplayPILImage(sample_img_portrait, x=10, y=20, image_width=100, image_height=200)

        lcd.expect_golden(self, "rev_c_display_pil_image_patch_portrait")

    def test_display_pil_image_patch_landscape(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.LANDSCAPE)
        lcd.DisplayPILImage(sample_img_landscape, x=10, y=20, image_width=100, image_height=200)

        lcd.expect_golden(self, "rev_c_display_pil_image_patch_landscape")

    def test_display_pil_image_patch_reverse_portrait(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.REVERSE_PORTRAIT)
        lcd.DisplayPILImage(sample_img_portrait, x=10, y=20, image_width=100, image_height=200)

        lcd.expect_golden(self, "rev_c_display_pil_image_patch_reverse_portrait")

    def test_display_pil_image_patch_reverse_landscape(self):
        lcd = MockedLcdCommRevC()
        lcd.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)
        lcd.DisplayPILImage(sample_img_landscape, x=10, y=20, image_width=100, image_height=200)

        lcd.expect_golden(self, "rev_c_display_pil_image_patch_reverse_landscape")

    # display_pil_image_offscreen_<orientation> : a partially offscreen image is clipped to the display

    @staticmethod
    def _new_5inch_lcd(orientation):
        lcd = MockedLcdCommRevC()
        # Normally detected by InitializeComm() from the display reply
        lcd.sub_revision = SubRevision.REV_5INCH
        lcd.rom_version = 88
        lcd.SetOrientation(orientation=orientation)
        return lcd

    def _expect_same_as_visible_crop(self, orientation, image, x, y, crop, crop_x, crop_y):
        start = Count.Start
        self.addCleanup(setattr, Count, "Start", start)

        clipped = self._new_5inch_lcd(orientation)
        Count.Start = 0
        clipped.DisplayPILImage(image, x=x, y=y)

        expected = self._new_5inch_lcd(orientation)
        Count.Start = 0
        expected.DisplayPILImage(image.crop(crop), x=crop_x, y=crop_y)

        self.assertEqual(clipped.lcd_serial.mock_calls, expected.lcd_serial.mock_calls)

    def test_display_pil_image_offscreen_top_left_portrait(self):
        image = sample_img_portrait.crop((0, 0, 100, 200))
        self._expect_same_as_visible_crop(Orientation.PORTRAIT, image, -30, -40, (30, 40, 100, 200), 0, 0)

    def test_display_pil_image_offscreen_bottom_right_landscape(self):
        image = sample_img_landscape.crop((0, 0, 100, 200))
        self._expect_same_as_visible_crop(Orientation.LANDSCAPE, image, 750, 400, (0, 0, 50, 80), 750, 400)

    def test_display_pil_image_fully_offscreen_sends_nothing(self):
        lcd = self._new_5inch_lcd(Orientation.LANDSCAPE)
        before = len(lcd.lcd_serial.mock_calls)
        lcd.DisplayPILImage(sample_img_landscape.crop((0, 0, 100, 200)), x=-150, y=10)
        self.assertEqual(len(lcd.lcd_serial.mock_calls), before)

