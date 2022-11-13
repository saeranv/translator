## TRANSLATE-LOCAL

Subtitle (.srt) translation from English to Tamil using mbart50_m2m.

## INSTALLATION-UBUNTU

To install EasyNMT:
`$ pip install -U easynmt`

Then this, if former doesn't work:
`$ pip install --no-deps easynmt`
`$ pip install tqdm transformers numpy nltk sentencepiece`

# INSTALLATION-WINDOWS

Follow instructions for Ubuntu, but also downgrade protobuf (as of 2022-11-12) with:
`$ pip install --upgrade "protobuf<=3.20.1"`

## TRANSLATE

python -m translate.app SRT_KEYWORD


### TODO
- sync batch_size with mbart
- convert .sh to python, ie: python -m translate.create_service_account $SA_NAME
