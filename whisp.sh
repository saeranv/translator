#!/bin/bash
WHISPD="/mnt/c/users/admin/masterwin/whisper.cpp"
TRANSD="/mnt/c/users/admin/masterwin/translator/"
transcl_sh="/home/saeranv/master/orgmode/auto/trans/trans.sh"
WHISPLOG=$TRANSD/whisp.log
HELPCMD () { 
helpstr=$(cat << EOF
USAGE: 
whisp -write [model=large|medium|small|base] [wav_fpath=*.wav] [kwargs='-l ta'] | tee [output_fpath=*.txt]
    * whisp -write small in.wav '-l tamil -tr english' | tee out.txt
    * the '| tee' redirect will overwrite existing files. 
    * kwarg options:
        * -l [english|tamil|auto]  # language DO NOT USE QUOTES
        * -tr  # translates to english
        * -nt  # no timestamps, note that timestamps will only appear in stdout 
               # so won't appear in fpath when use -otxt option
               # thus idiomatic whisp.sh uses redirect stdout to file ie. | tee out.txt
        * -pc  # print-colors (probability). This will print charkeys to 
               # stdout, so don't use if you are redirecting to file.
        * use 'whisp - -h or whisp -readme' to see more arg options
whisp -stream [model=small|etc] [kwargs='-c 2 -vth 0.6 --length 10000 -t 4 -l tamil -tr -f ./whisp.txt']
    * whisp -stream small '-c 2 -vth 0.6 --step 5000 --length 10000 -t 4 -l tamil -tr -f ./whisp.txt'
    * kwarg options:
        * -c [id]  # device id, find by running '$ lsusb' or 'python -m translator.micvad'
        * -l [english|tamil|auto]  # language (don't use quotes ie. -l 'auto')
        * -tr # translates to english
        * -nt # no timestamps
        * -f [text_fpath]  # text file to write to
        * -t [int]  # threads
        * --length [int]  # length in ms
        * --step [int]    # step size in ms <= lenght, if 0, uses VAD when voice detected.  
        * -vth [float]  # vad threshold, only used if --step 0 (I think...)
whisp -stream-ez [model=small] [**kwargs]  # stream with fixed params, no args.
    * whisp -stream-ez small
whisp -play <wavfpath> # playback of audio file, <ESC> to stop.
    * whisp -play in.wav
whisp -snip [in_wavfpath=*.wav] [out=*.wav] [start_time=HH:MM:SS] [end_time=HH:MM:SS]  
    * whisp -snip in.wav snipped.wav "00:00:43" "00:01:30" 
whisp -stream-log 
    * whisp -stream-log | tail -5 | transcl -b en:ta 2> /dev/null # translates ./whisp.log
whisp -extract <mp4fpath>  # Extracts audio mp3 from mp4
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
elif [[ "$1" == "-write" ]]; then
    model=$( python -c "print('models/ggml-' + '${2}'.strip() + '.bin');" )
    wavfpath=$3
    kwargs=$( python -c "import sys; print(*sys.argv[4:])" "${@}" ) 
    echo "Check args:" >&2  
    printf "\t-model=${model}\n" >&2
    printf "\t-wav=${wavfpath}\n" >&2 
    printf "\t-kwargs='${kwargs}'\n" >&2
    read -n 1 -p "Continue (y/n)? " choice
    [[ $choice != "y" ]] && printf "\nExiting.\n" && exit 1 || printf "\nContinuing..\n"
    
    $WHISPD/main $kwargs -m "${WHISPD}/${model}" --file $wavfpath
elif [[ "$1" == "-stream" ]]; then
    model=$( python -c "print('models/ggml-' + '${2}'.strip() + '.bin');" )
    kwargs=$( python -c "import sys; print(sys.argv[3:])" ) "${@}"
    echo "Check args:" >&2
    printf "\t-model=${model}\n" >&2
    printf "\t-kwargs='${kwargs}'\n" >&2 
    read -n 1 -p "Continue (y/n)? " choice
    [[ $choice != "y" ]] && printf "\nExiting.\n" && exit 1 || printf "\nContinuing..\n"
    # current models in ./models: "ggml-large.bin", "ggml-base.bin"
    #./stream -m ./models/ggml-base.bin -t 16 -c 2 -l english -vth 0.9
    # longer --step 10000 --lenght 20000 # improves accuracy 
    # larger model is slower but more accurate, only works with large step/lenght (10000, 20000)
    # -vth = higher values detects silence more often 
    #--length 5000 \
    $WHISPD/stream $kwargs -m "${WHISPD}/${model}" 
elif [[ "$1" == "-stream-ez" ]]; then
    echo "# ${WHISPLOG}" >| $WHISPLOG   # clear whisp.log
    model=$( python -c "print('models/ggml-' + '${2}'.strip() + '.bin');" )
    kwargs=$( python -c "import sys; print(sys.argv[3:])" ) "${@}"
    echo "Check args:" >&2
    printf "\t-model=${model}\n" >&2
    printf "\t-kwargs='${kwargs}'\n" >&2 
    read -n 1 -p "Continue (y/n)? " choice
    [[ $choice != "y" ]] && printf "\nExiting.\n" && exit 1 || printf "\nContinuing..\n"
    $WHISPD/stream -m "${WHISPD}/${model}" \
        -t 4 --step 0 --length 10000 \
        -l ta -vth 0.6 -f $WHISPLOG $kwargs
elif [[ "$1" == "-stream-log" ]]; then
    cat $WHISPLOG
elif [[ "$1" == "-play" ]]; then
    ffplay "$2"
elif [[ "$1" == "-snip" ]]; then 
    input_file="$2"
    output_file="$3"
    start_time="$4"
    end_time="$5"
    echo "Check args:" >&2
    printf "\t-input_fpath=${input_file}\n" >&2
    printf "\t-output_fpath='${output_file}'\n" >&2 
    printf "\t-start_time='${start_time}'\n" >&2 
    printf "\t-end_time='${end_time}'\n" >&2 
    read -n 1 -p "Continue (y/n)? " choice
    [[ $choice != "y" ]] && printf "\nExiting.\n" && exit 1 || printf "\nContinuing..\n"
    
    ffmpeg -i "${input_file}" -ss "${start_time}" -to "${end_time}" -c copy "${output_file}"
    echo "Snipped file at ${output_file}"
elif [[ "$1" == "-extract" ]]; then
    mp4f=$2 
    mp3f=$( python -c "print('${mp4f}'.replace('.mp4', '.mp3'))" )
    wavf=$( python -c "print('${mp4f}'.replace('.mp4', '.wav'))" )
    echo "Check args:" >&2
    printf "\t-mp4_fpath=${mp4f}\n" >&2
    printf "\t-mp3_fpath=${mp3f}\n" >&2
    printf "\t-wav_fpath=${wavf}\n" >&2
    read -n 1 -p "Continue (y/n)? " choice
    [[ $choice != "y" ]] && printf "\nExiting.\n" && exit 1 || printf "\nContinuing..\n"
    
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
fi


