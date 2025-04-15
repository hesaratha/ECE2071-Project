import os
import serial
import wave
import serial.tools.list_ports

SAMPLE_RATE = 5000
DURATION_SEC = 10
NUM_SAMPLES = SAMPLE_RATE * DURATION_SEC
BAUD_RATE = 115200
BASE_FILENAME = "recording"
EXTENSION = ".wav"
FILENAME_FORMAT = "{base}_{index}{ext}"


def find_stm_port():
    for port in serial.tools.list_ports.comports():
        if "STM" in port.description:
            return port.device
    return None


def get_unique_filename(base, ext):
    index = 0
    while os.path.exists(FILENAME_FORMAT.format(base=base, index=index, ext=ext)):
        index += 1
    return FILENAME_FORMAT.format(base=base, index=index, ext=ext)


def main():
    print("Searching for STM32 device...")
    stm_port = find_stm_port()
    if not stm_port:
        print("ERROR: No STM32 device found.")
        return

    filename = get_unique_filename(BASE_FILENAME, EXTENSION)
    print(f"Device found on {stm_port}.")

    print(f"\nStarting audio recording:")
    print(
        f"\tDuration: {DURATION_SEC} seconds\n\tSample Rate: {SAMPLE_RATE} Hz\n\tTotal Samples: ({NUM_SAMPLES} bytes)\n")

    with serial.Serial(stm_port, BAUD_RATE, timeout=1) as ser:
        data = bytearray()
        last_printed_percent = -1

        while len(data) < NUM_SAMPLES:
            byte = ser.read(1)
            if byte:
                data.append(byte[0])

            percent = int(len(data) / NUM_SAMPLES * 100)
            if percent != last_printed_percent:
                print(f"\rProgress: {percent}%", end="")
                last_printed_percent = percent
    print(f"\nAudio recording completed successfully.")

    print(f"\nWriting audio data to file: {filename}")

    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(1)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(data)

    print("File saved successfully.")


if __name__ == "__main__":
    main()
