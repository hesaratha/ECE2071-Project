from pathlib import Path
from typing import Optional, Tuple, TypeVar

import matplotlib.pyplot as plt
import numpy as np
import serial
import serial.tools.list_ports as list_ports
from scipy.io import wavfile

T = TypeVar("T")

SAMPLE_RATE = 22_050
BAUD_RATE = 921_600
BASE_FILENAME = "recording"

MODE_OPTIONS: dict[int, Tuple[str, bytes]] = {
    1: ("Manual", b"0"),
    2: ("Distance Trigger", b"1"),
}

FILE_FORMATS: dict[int, str] = {
    1: ".wav",
    2: ".png",
    3: ".csv",
}


def find_stm_port() -> Optional[str]:
    """Locate the STM32 serial port by matching its description."""
    for port in list_ports.comports():
        if "STM" in port.description:
            return port.device
    return None


def get_unique_filename(base: str, ext: str) -> Path:
    """Generate a non-colliding filename by appending an index."""
    index = 0
    path = Path(f"{base}_{index}{ext}")
    while path.exists():
        index += 1
        path = Path(f"{base}_{index}{ext}")
    return path


def display_menu(options: dict[int, str], title: Optional[str] = None) -> None:
    """Print a numbered menu to stdout."""
    if title:
        print(title)
        print("-" * len(title))
    for key, label in options.items():
        print(f"{key}: {label}")


def get_choice(options: dict[int, T], prompt: str = "Select an option") -> T:
    """Prompt until a valid numeric selection is made."""
    while True:
        try:
            choice = int(input(f"{prompt}: "))
            if choice in options:
                return options[choice]
            print("ERROR: Invalid choice")
        except ValueError:
            print("ERROR: Please enter a number")
        except KeyboardInterrupt:
            print()
            exit(0)


def record_manual(
        port: str,
        baud_rate: int,
        mode_cmd: bytes,
        sample_count: int,
) -> np.ndarray:
    """Record a fixed number of audio samples from the STM32 device."""
    with serial.Serial(port, baud_rate, timeout=1) as ser:
        ser.write(mode_cmd)
        samples = np.empty(sample_count, dtype=np.uint8)
        count = 0
        last_percent = -1

        while count < sample_count:
            byte = ser.read(1)
            if byte:
                samples[count] = byte[0]
                count += 1
            percent = count * 100 // sample_count
            if percent != last_percent:
                print(f"\rProgress {percent}%", end="", flush=True)
                last_percent = percent
    print()
    return samples


def record_distance_trigger(
        port: str,
        baud_rate: int,
        mode_cmd: bytes,
) -> np.ndarray:
    """Record audio samples until interrupted by the user."""
    with serial.Serial(port, baud_rate, timeout=1) as ser:
        ser.write(mode_cmd)
        buffer: list[int] = []
        last_len = 0
        try:
            while True:
                byte = ser.read(1)
                if byte:
                    buffer.append(byte[0])
                length = len(buffer)
                if length != last_len:
                    print(f"\rRecorded bytes {length}", end="", flush=True)
                    last_len = length
        except KeyboardInterrupt:
            print()
        return np.frombuffer(bytes(buffer), dtype=np.uint8)


def record_audio(
        port: str,
        baud_rate: int,
        mode_cmd: bytes,
        sample_count: Optional[int] = None,
) -> np.ndarray:
    """Dispatch recording based on mode: fixed count or triggered."""
    if sample_count is None:
        return record_distance_trigger(port, baud_rate, mode_cmd)
    return record_manual(port, baud_rate, mode_cmd, sample_count)


def save_wav(filename: Path, samples: np.ndarray, sample_rate: int) -> None:
    """Save samples to a WAV file with appropriate PCM format."""
    wavfile.write(str(filename), sample_rate, samples)


def save_png(filename: Path, samples: np.ndarray, sample_rate: int) -> None:
    """Plot audio waveform and save as PNG."""
    times = np.arange(samples.size) / sample_rate
    plt.figure()
    plt.plot(times, samples, linewidth=0.2)
    plt.title('Audio Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.savefig(str(filename))
    plt.close()


def save_csv(filename: Path, samples: np.ndarray, sample_rate: int) -> None:
    """Export samples to a CSV with sample rate header."""
    np.savetxt(str(filename), samples, header=f"Sample rate {sample_rate} Hz", fmt='%d')


def choose_recording_mode() -> Tuple[bytes, Optional[int]]:
    """Prompt user to select recording mode and duration if manual."""
    display_menu({k: v[0] for k, v in MODE_OPTIONS.items()}, title="Recording Modes")
    _, mode_cmd = get_choice(MODE_OPTIONS, prompt="Choose mode")
    if mode_cmd == b"0":
        while True:
            try:
                seconds = float(input("Enter duration in seconds: "))
                return mode_cmd, int(seconds * SAMPLE_RATE)
            except ValueError:
                print("ERROR: Invalid number")
    return mode_cmd, None


def choose_output_format() -> str:
    """Prompt user to select output file format."""
    display_menu(FILE_FORMATS, title="Output Formats")
    return get_choice(FILE_FORMATS, prompt="Choose file type")


def run_cli(port: str) -> None:
    """Main interactive loop: select mode, record, and save."""
    while True:
        mode_cmd, count = choose_recording_mode()
        ext = choose_output_format()
        filename = get_unique_filename(BASE_FILENAME, ext)

        print(f"Recording to {filename}")
        samples = record_audio(port, BAUD_RATE, mode_cmd, count)

        print(f"Saving to {filename}")
        match ext:
            case '.wav':
                save_wav(filename, samples, SAMPLE_RATE)
            case '.png':
                save_png(filename, samples, SAMPLE_RATE)
            case '.csv':
                save_csv(filename, samples, SAMPLE_RATE)

        print("File saved successfully.")


def main() -> None:
    """Discover STM32 port and start the CLI recorder."""
    port = find_stm_port()
    if port is None:
        print("ERROR: No STM32 device found")
        return
    print(f"STM32 device found on {port}")
    run_cli(port)


if __name__ == '__main__':
    main()
