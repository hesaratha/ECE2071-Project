import serial
import wave
import serial.tools.list_ports

# Configuration
SAMPLE_RATE = 5000
DURATION_SEC = 10
NUM_SAMPLES = SAMPLE_RATE * DURATION_SEC
BAUD_RATE = 115200
OUTPUT_FILENAME = "processed_audio.wav"


def find_stm_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # You can print p.description or p.manufacturer to see how your device is identified
        if "STM" in p.description:
            return p.device
    # If no suitable port is found, return None (or raise an exception)
    return None


def main():
    stm_port = find_stm_port()
    if not stm_port:
        print("No STM32 device found. Please plug in your device or update the search filter.")
        return

    print(f"Opening serial port: {stm_port}")
    with serial.Serial(stm_port, BAUD_RATE, timeout=1) as ser:
        print(f"Recording {DURATION_SEC} seconds of audio at {SAMPLE_RATE} Hz...")
        data = bytearray()

        while len(data) < NUM_SAMPLES:
            byte = ser.read(1)
            if byte:
                data.extend(byte)
                print(f"\rReceived: {len(data)} /", NUM_SAMPLES, end=" bytes")

        print(f"\nCaptured {len(data)} bytes. Writing to {OUTPUT_FILENAME}...")

        with wave.open(OUTPUT_FILENAME, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(1)  # 8-bit
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(data)

    print("Done.")


if __name__ == "__main__":
    main()
