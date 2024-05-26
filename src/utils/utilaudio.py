import sounddevice as sd

from utils.utilconfig import load_ini_section, find_path, ConfigName
from utils.utillog import MyLog

my_log = MyLog()

_audio: dict[str, str] = load_ini_section(find_path(ConfigName.main_ini), "AUDIO")
SD_NAME: str = _audio.get("device_name", "USB Audio").strip()
assert SD_NAME
# noinspection PyBroadException
try:
    dev_in: dict[str, any] = sd.query_devices(SD_NAME, kind='input')
    dev_out: dict[str, any] = sd.query_devices(SD_NAME, kind='output')
    sd.default.device = SD_NAME
    my_log.info(f"Found device matching name: {SD_NAME}")
except Exception:
    my_log.error(f"No device matching name: {SD_NAME}, using default audio device instead")
    dev_in: dict[str, any] = sd.query_devices(None, kind='input')
    dev_out: dict[str, any] = sd.query_devices(None, kind='output')

my_log.debug(f"Using IN/OUT devices:\n{dev_in}\n\n{dev_out}")

# =======================================
if dev_in["max_input_channels"] not in [1, 2]:
    raise RuntimeError(f"ALSA IN device must have 1 or 2 channels, got {dev_in['max_input_channels']}")
if dev_out["max_output_channels"] not in [1, 2]:
    raise RuntimeError(f"ALSA OUT device must have 1 or 2 channels, got {dev_out['max_output_channels']}")
# make all mono if IN or OUT is mono
SD_CH = min(dev_in["max_input_channels"], dev_out["max_output_channels"])
sd.default.channels = SD_CH, SD_CH

# ===============================================

SD_RATE: int = sd.default.samplerate
if not SD_RATE:
    SD_RATE = 44100
    sd.default.samplerate = SD_RATE

# =============================================
SD_TYPE: str = _audio.get("device_type", "float32").strip()
assert SD_TYPE
if SD_TYPE not in ['int16', 'float32']:
    raise RuntimeError(f"ALSA device must have data type in16 or float32, got {SD_TYPE}")
# noinspection PyBroadException
if sd.default.dtype != (SD_TYPE, SD_TYPE):
    sd.default.dtype = (SD_TYPE, SD_TYPE)

my_log.info(f"Had set device type: {SD_TYPE}")
# =========================================
MAX_LEN = _audio.get('max_len_seconds', '60')
if not MAX_LEN.isdigit():
    MAX_LEN = 60
else:
    MAX_LEN = int(MAX_LEN)

assert MAX_LEN and isinstance(MAX_LEN, int)
MAX_LEN = MAX_LEN * SD_RATE
# =========================================

sd.default.latency = ('low', 'low')
my_log.info(f"Using IN/OUT channels: {SD_CH}, sample rate: {SD_RATE}")

sd.check_output_settings(channels=SD_CH, dtype=SD_TYPE, samplerate=SD_RATE)
sd.check_input_settings(channels=SD_CH, dtype=SD_TYPE, samplerate=SD_RATE)

# =============================================

tmp = _audio.get("drum_volume", "1.0")
DRUM_VOLUME: float = 1.0
# noinspection PyBroadException
try:
    DRUM_VOLUME = float(tmp)
    DRUM_VOLUME = min(DRUM_VOLUME, 1.0)
    DRUM_VOLUME = max(DRUM_VOLUME, 0.1)
except Exception:
    my_log.error(f"Value of drum_volume is incorrect in main.ini file: {tmp}, using value of 1.0")
