## TRANSLATE
Tools for translation.

### WHISPER-AUDIO
#### whisp.sh transcribes audio to text.
$ ./whisp.sh -h  # for usage
- TRANSCRIBE to .txt
    - transcribes in tamil (but not tamil/english mixed)
    - translates .wav from <lang> to english. Not sure if other way is possible
- EXTRACTS audio from .mp4 to .wav format
#### TODO
- STREAM audio to text
- TRANSCRIBE to .srt, is built-into whisper.cpp apparently.


### TRANSLATE-TEXT
#### transl.sh translates text.
python -m translator.srt -k SRT_KEYWORD -i INCLUDE_EN -c CHUNK_SIZE
python -m translator.translator "translate me"

### MICVAD
#### micvad transcribes text stream from mic audio via deepspeech.
python -m micvad.audio  # to get connected audio device data
. mic.sh {VAD=3} {DEVICE-ID=1} {SAMPLE-RATE=44100} {ENGLISH-RECORD=1}


### INSTALLATION
#### WHISP-UBUNTU
`$ sudo ./whisp_install.sh` 

### WSL2-USB-MIC
$ sudo ./usbipd_install.sh
- then go here and follow instructions to register usb from powershell to wsl2: 
  https://learn.microsoft.com/en-us/windows/wsl/connect-usb


#### EASYNMT-UBUNTU
To install EasyNMT:
`$ pip install -U easynmt`
Then this, if former doesn't work:
`$ pip install --no-deps easynmt`
`$ pip install tqdm transformers numpy nltk sentencepiece`

#### EASYNMT-WINDOWS
Follow instructions for Ubuntu, but also downgrade protobuf (as of 2022-11-12) with:
`$ pip install --upgrade "protobuf<=3.20.1"`

### DEEPSPEECH-GPU
(requires cuda 10.1)
OS: Windows 10 Pro, 64-bit
NVIDIA GeForce RTX 2080
- driver version: 512.78
- supports CUDA 11.6
