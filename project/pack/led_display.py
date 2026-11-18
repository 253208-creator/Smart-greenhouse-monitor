import framebuf, time


class OLED:
    def __init__(self, width, height, i2c, address):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.address = address
        self.offset = 2

        self.buffer = bytearray(width * height // 8)

        self.fb = framebuf.FrameBuffer(
            self.buffer,
            width,
            height,
            framebuf.MONO_VLSB
        )

        self.init_display()

    def command(self, cmd):
        self.i2c.writeto(
            self.address,
            bytes([0x00, cmd])
        )

    def init_display(self):
        time.sleep_ms(100)

        commands = [
            0xAE,       # Display OFF
            0xD5, 0x80, # Clock
            0xA8, 0x3F, # Multiplex ratio
            0xD3, 0x00, # Display offset
            0x40,       # Start line
            0xAD, 0x8B, # DC-DC control
            0xA1,       # Segment remap
            0xC8,       # COM scan direction
            0xDA, 0x12, # COM pins
            0x81, 0xCF, # Contrast
            0xD9, 0xF1, # Precharge
            0xDB, 0x40, # VCOM
            0xA4,       # Display follows RAM
            0xA6,       # Normal display
            0xAF        # Display ON
        ]

        for cmd in commands:
            self.command(cmd)

        self.fill(0)
        self.show()

    def show(self):
        for page in range(8):
            self.command(0xB0 + page)
            self.command(0x02)
            self.command(0x10)

            start = page * 128
            data = self.buffer[start:start + 128]

            self.i2c.writeto(
                self.address,
                b'\x40' + data
            )

    def fill(self, color):
        self.fb.fill(color)

    def text(self, string, x, y, color=1):
        self.fb.text(string, x, y, color)

    def pixel(self, x, y, color=1):
        self.fb.pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color=1):
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color=1):
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        self.fb.fill_rect(x, y, w, h, color)

    def hline(self, x, y, w, color=1):
        self.fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        self.fb.vline(x, y, h, color)