#!/bin/bash
WHISPD="/mnt/c/users/admin/masterwin/whisper.cpp"
TRANSD="/mnt/c/users/admin/masterwin/translator/"
transcl_sh="/home/saeranv/master/orgmode/auto/trans/trans.sh"
WHISPLOG=$TRANSD/whisp.log
HELPCMD () { 
helpstr=$(cat << EOF
USAGE: 
whisp -write -model=[large|base] -kwargs='[-tr|-nt]' in.wav | tee out.txt
ie. whisp -write -model=base -kwargs='-l tamil -tr english' in.wav | tee out.txt
Note: '| tee' redirect will overwrite existing files.   
* For kwargs use 'whisp - -h or whisp -readme' to see arg options. Examples:
    * -l [english|tamil|auto]  # language DO NOT USE QUOTES
    * -tr  # translates to english
    * -nt  # no timestamps, note that timestamps will only appear in stdout 
           # so won't appear in fpath when use -otxt option
           # thus idiomatic whisp.sh uses redirect stdout to file ie. | tee out.txt
    * -pc  # print-colors (probability). This will print charkeys to 
           # stdout, so don't use if you are redirecting to file.
whisp -stream -model=small -c=2 -kwargs='-vth 0.6 --length 10000 -t 4 -l tamil -tr -f ./whisp.txt'
    * -c [id]  # device id, find by running '$ lsusb'
whisp -stream-ez -model=small [**kwargs]  # stream with fixed params, no args.
whisp -stream-log | tail -5 | transcl -b en:ta 2> /dev/null # translates ./whisp.log
whisp -play <wavfpath> # playback of audio file, <ESC> to stop.
whisp -extract <mp4fpath>  # Extracts audio mp3 to mp4
whisp -vim  # opens this .sh file
whisp -readme  # whisper.cpp readme (which has the --help text)
whisp -  # raw whisper.cpp, equal to \$\whispd/main arg1 arg2 ... 
OTHER:
\$\whispd is directory to whisper.cpp 
\$\whispw is ./samples/jfk.wav (for testing) 
EOF
)
echo "${helpstr}"; 
}

if [[ $"$1" == "-h" ]]; then
HELPCMD
elif [[ "$1" == "-write" ]] && [[ "$#" -eq 4 ]]; then
ln1="arg='${2}'; assert '-model' in arg; model=arg.split('=')[1];" 
ln2="print('models/ggml-' + model + '.bin');"
model=$( python -c "${ln1} ${ln2}" )
ln1="arg='${3}'; assert '-kwargs' in arg; print(arg.split('=')[1]);" 
kwargs=$( python -c "${ln1}" )
wavfpath=$4
echo "whisp.sh args:" >&2  
printf "\t-wav=${wavfpath}\n" >&2 
printf "\t-model=${model}\n" >&2
printf "\t-kwargs='${kwargs}'\n" >&2 
# current models in ./models: "ggml-large.bin", "ggml-base.bin"
$WHISPD/main $kwargs \
    --model "${WHISPD}/${model}" --file $wavfpath
elif [[ "$1" == "-stream" ]]; then
ln1="arg='${2}'; assert '-model' in arg; model=arg.split('=')[1];" 
ln2="print('models/ggml-' + model + '.bin');"
model=$( python -c "${ln1} ${ln2}" )
ln1="arg='${3}'; assert '-c' in arg; print(arg.split('=')[1]);" 
device_id=$( python -c "${ln1}" )
ln1="arg='${4}'; assert '-kwargs' in arg; print(arg.split('=')[1]);" 
kwargs=$( python -c "${ln1}" )
echo "whisp.sh args:" >&2
printf "\t-model=${model}\n" >&2
printf "\t-device='${device_id}'\n" >&2 
printf "\t-kwargs='${kwargs}'\n" >&2 
# current models in ./models: "ggml-large.bin", "ggml-base.bin"
#./stream -m ./models/ggml-base.bin -t 16 -c 2 -l english -vth 0.9
# longer --step 10000 --lenght 20000 # improves accuracy 
# larger model is slower but more accurate, only works with large step/lenght (10000, 20000)
# -vth = higher values detects silence more often 
#--length 5000 \
$WHISPD/stream -m "${WHISPD}/${model}" \
    -c "${device_id}" $kwargs
elif [[ "$1" == "-stream-ez" ]]; then
echo "# ${WHISPLOG}" >| $WHISPLOG
ln1="arg='${2}'; assert '-model' in arg; model=arg.split('=')[1];" 
ln2="print('models/ggml-' + model + '.bin');"
model=$( python -c "${ln1} ${ln2}" )
echo "whisp.sh args:" >&2
printf "\t-model=${model}\n" >&2
$WHISPD/stream -m "${WHISPD}/${model}" \
    -t 4 --step 0 --length 10000 \
    -l ta -vth 0.6 -f $WHISPLOG "${@:3}" #>/dev/null & #2>&1 &
## Translate 
#while true; do
#    echo "-----" 
#    cat $WHISPLOG | tail -5 | $transcl_sh -b ta:en
#    sleep 10
#done
elif [[ "$1" == "-stream-log" ]]; then
    cat $WHISPLOG
elif [[ "$1" == "-play" ]]; then
    ffplay "$2"
elif [[ "$1" == "-extract" ]]; then
    mp4f=$2 
    mp3f=$( python -c "print('${mp4f}'.replace('.mp4', '.mp3'))" )
    wavf=$( python -c "print('${mp4f}'.replace('.mp4', '.wav'))" )
    printf "Converting ${mp4f} to mp3 at ${mp3f}.\n" 
    ffmpeg -i "$mp4f" -vn "$mp3f"
    printf "Converting ${mp3f} to wav at ${wavf}.\n" 
    ffmpeg -i $mp3f -ar 16000 -ac 1 -c:a pcm_s16le $wavf
    rm -f $mp3f
    echo "Remove ${mp3f}"
    echo $wavf
elif [[ "$1" == "-vim" ]]; then
    nvim $masterwin/translator/whisp.sh;
elif [[ "$1" == "-" ]]; then
    args="${@:2}"
    $WHISPD/main $args
elif [[ "$1" == "-readme" ]]; then
    cat $WHISPD/readme.md
else
    echo "Invalid: ${@}"
    printf "Check "
    HELPCMD
fi


