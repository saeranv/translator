#!/bin/bash
modeldir=$PWD/../models
vad=$1
device=$2
rate=$3
python mic_vad_streaming.py -m $modeldir/deepspeech-0.9.3-models.pbmm -s $modeldir/deepspeech-0.9.3-models.scorer --nospinner -v $vad -d $device -r $rate
