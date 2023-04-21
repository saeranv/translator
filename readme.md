## TRANSLATE-LOCAL
Tools for translation.

### INSTALLATION-UBUNTU
To install EasyNMT:
`$ pip install -U easynmt`

Then this, if former doesn't work:
`$ pip install --no-deps easynmt`
`$ pip install tqdm transformers numpy nltk sentencepiece`

### INSTALLATION-WINDOWS
Follow instructions for Ubuntu, but also downgrade protobuf (as of 2022-11-12) with:
`$ pip install --upgrade "protobuf<=3.20.1"`

### TRANSLATE
python -m translator.srt -k SRT_KEYWORD -i INCLUDE_EN -c CHUNK_SIZE
python -m translator.translator "translate me"

### VAD 		
python -m micvad.audio  # to get connected audio device data
. mic.sh {VAD=3} {DEVICE-ID=1} {SAMPLE-RATE=44100} {ENGLISH-RECORD=1}


### WHISPER
. ./whisp.sh -h  # for usage
# TODO: can transcribe... but currently not working
# TODO: can record and extract audio using ffmpeg


### DEEPSPEECH-GPU
(requires cuda 10.1)
OS: Windows 10 Pro, 64-bit
NVIDIA GeForce RTX 2080
- driver version: 512.78
- supports CUDA 11.6
