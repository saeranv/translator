#!/bin/bash
WHISPD="/mnt/c/users/admin/masterwin/whisper.cpp"
HELPSTR=$(cat << EOF
Usage: 
    whisp -write -model=[large|base] -kwargs='[-tr|-nt]' in.wav in.txt 
    * <txtfpath> MUST be .txt
    * For kwargs use 'whisp - -h' for args. Enclose all in str.
        * -l [english|tamil|auto]  # language DO NOT USE QUOTES
        * -tr  # translates to english
        * -nt  # no timestamps, but timestamps will only appear in stdout
               # so better to just whisp -write ... >| out.txt  
        * -pc  # print-colors (probability)
        * can do multiple i,e -kwargs='-tr -tn -pc -l tamil'
    whisp -play <wavfpath> # playback of audio file, <ESC> to stop.
    whisp -extract <mp4fpath>  # Extracts audio mp3 to mp4
    whisp -vim  # opens this .sh file
    whisp -readme  # whisper.cpp readme (which has the --help text)
    whisp -  # raw whisper.cpp, equal to \$\whispd/main arg1 arg2 ... 
Other:
    \$\whispd is directory to whisper.cpp 
    \$\whispw is ./samples/jfk.wav (for testing) 
EOF
) 

if [[ "$#" -eq 0 ]] || [[ $"$1" == "-h" ]]; then
    echo "${HELPSTR}"
elif [[ "$1" == "-write" ]] && [[ "$#" -gt 3 ]]; then
    ln1="arg='${2}'; assert '-model' in arg; model=arg.split('=')[1];" 
    ln2="print('models/ggml-' + model + '.bin');"
    model=$( python -c "${ln1} ${ln2}" )
    ln1="arg='${3}'; assert '-kwargs' in arg; print(arg.split('=')[1]);" 
    kwargs=$( python -c "${ln1}" )
    wavfpath=$4
    if [[ "$#" -eq 5 ]]; then
        ln1="import os; arg='${5}'; assert '.txt' in arg;"
        #ln2="arg=os.path.abspath(arg);"
        ln3="print(arg.replace('.txt', ''));"
        txtfpath=$( python -c "${ln1} ${ln3}" )
    else
        txtfpath=$5
    fi
    echo "whisp.sh args:" >&2  
    printf "\t-wav=${wavfpath}\n" >&2 
    printf "\t-txt=${txtfpath}.txt\n" >&2 
    printf "\t-model=${model}\n" >&2
    printf "\t-kwargs='${kwargs}'\n" >&2 
    echo "Transcribing ./$( basename ${wavfpath} ) to ./$(basename ${txtfpath}).txt" 
    # current models in ./models: "ggml-large.bin", "ggml-base.bin"
    #--output-txt --output-file $txtfpath \
    $WHISPD/main $kwargs \
        --model "${WHISPD}/${model}" --file $wavfpath
elif [[ "$1" == "-play" ]]; then
    ffplay "$2"
elif [[ "$1" == "-stream" ]]; then
    echo "Not implemented" 
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
fi


