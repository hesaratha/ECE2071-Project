import os
import serial
import wave
import serial.tools.list_ports
import matplotlib.pyplot as plt
import numpy as np

SAMPLE_RATE = 5000
BAUD_RATE = 115200
BASE_FILENAME = "recording"
FILENAME_FORMAT = "{base}_{index}{ext}"

modeOptions = {
    1: "Manual Recording Mode",
    2: "Distance Trigger Mode"
}

ouputOptions = {
    1: ".wav",
    2: ".png",
    3: ".csv"
}

currentChoice = None

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

stm_port = find_stm_port()

def display_menu(menu):
    """Displays menu with available modes
    parameters: dictionary to display
    no returns:
    """
    if menu == modeOptions:
        print("Main Menu")
        print("-------------------------")
        for key, value in menu.items():
            print(f"{key}: {value} Mode")
        print("Press Ctrl+C to quit")
    else:
        print("Select file Type")
        for key, value in menu.items():
            print(f"{key}: {value}")

def quit_program():
    """
    exits program
    parameters:
    returns:
    """
    print("\nShutting Down...\n")
    exit(0)

def get_sample_Duration():
    """
    gets user input float for sample duration
    parameters: round(float(input("Sample Duration: ")),3)
    returns float sample duration to 3dp
    """
    while True:
        try:
            sampleDuration = round(float(input("Sample Duration: ")),3) # round just in case the user asks for some ridiculous precision that exceeds the precision of our sample rate
            return sampleDuration
        except ValueError:
                print("Error: Length entered was not a number")

def make_wav_file(filename, data):
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(1)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(data)

def make_png_file(filename, data, numSamples):
    time = np.arange(0, numSamples)/SAMPLE_RATE
    amplitude = np.array(data)
    plt.plot(time,amplitude, linewidth = 0.2)
    plt.title("Audio Data")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.savefig(filename)
    #plt.show()

def manual_recording_mode():
    print("\nMaunual Recording Mode:")
    
    sampleDuration = get_sample_Duration()
    numSamples = int(sampleDuration*SAMPLE_RATE)

    display_menu(ouputOptions)
    fileType = ouputOptions[get_menu_choice(ouputOptions)]
    filename = get_unique_filename(BASE_FILENAME, fileType) 

    print(f"\nStarting audio recording:")
    print(
        f"\tDuration: {sampleDuration} seconds\n\tSample Rate: {SAMPLE_RATE} Hz\n\tTotal Samples: ({numSamples} bytes)\n")

    with serial.Serial(stm_port, BAUD_RATE, timeout=1) as ser:
        data = bytearray()
        last_printed_percent = -1

        while len(data) < numSamples:
            byte = ser.read(1)
            if byte:
                data.append(byte[0])

            percent = int(len(data) / numSamples * 100)
            if percent != last_printed_percent:
                print(f"\rProgress: {percent}%", end="")
                last_printed_percent = percent

    print(f"\nAudio recording completed successfully.")
    print(f"\nWriting audio data to file: {filename}")

    if fileType == ".wav":
        make_wav_file(filename, data)
    elif fileType == ".png":
        make_png_file(filename, data, numSamples)
    else:
        np.savetxt(filename,data,header=f"Sample rate is: {SAMPLE_RATE} sps")

    print("File saved successfully.")

def distance_trigger_mode():
    quit_program() #placeholder

def get_menu_choice(menu) -> int:
    """gets user input for menu choices
    parameters: input(option:)
    no returns
    """
    while True:
        try:
            choice = int(input("Option: "))
            if choice in menu.keys():
                return choice
            else:
                print("Error: Invalid option")
        except ValueError:
            print("Error: Only numbers are accepted")
        except KeyboardInterrupt:
            quit_program()
        except RuntimeError:
            quit_program()

def change_mode(choice):
    """allows user to change mode
    parameters: user input
    no returns
    """
    global currentChoice
    if not currentChoice == choice:
        match choice:
            case 1:
                manual_recording_mode()
            case 2:
                distance_trigger_mode()

def run_menu(menu):
    """displays main menu
    no parameters
    no returns
    """
    while True:
        display_menu(menu)
        mode = get_menu_choice(menu)
        change_mode(mode)

def main():
    print("Searching for STM32 device...")
    
    if not stm_port:
        print("ERROR: No STM32 device found.")
        return
    
    print(f"Device found on {stm_port}.")

    while True:
        run_menu(modeOptions)

if __name__ == "__main__":
    main()
