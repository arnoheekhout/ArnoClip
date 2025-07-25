# step1: Recognize
python videoclipper.py --stage 1 \
                       --file ../examples/2022 Yunqi Conference_Segment.mp4 \
                       --sd_switch yes \
                       --output_dir ./output
# now you can find recognition results and entire SRT file in ./output/
# step2: Clip
python videoclipper.py --stage 2 \
                       --file ../examples/2022 Yunqi Conference_Segment.mp4 \
                       --output_dir ./output \
                       --dest_text 'So this is our original intention for establishing this award, and we will continue to hold it session after session' \
                    #    --dest_spk spk0 \
                       --start_ost 0 \
                       --end_ost 100 \
                       --output_file './output/res.mp4'
