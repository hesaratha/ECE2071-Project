import numpy as np 
import wave
import serial
import serial.tools.list_ports 

# devices = serial.tools.list_ports.comports()

# for element in devices:
#     print(element)


SAMPLE_RATE = 5000
ser = serial.Serial("COM7", 115200)
data = []
fileName = "wav_file.wav"

for i in range(5*SAMPLE_RATE):
    single_data = ser.read(1).decode()
    data.append(single_data[0])

# print(data)

data = np.array(data)

data = (data - data.min())/ data.max()

data = data.astype(np.uint8)

with wave.open(fileName, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(1)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(data.tobytes())



