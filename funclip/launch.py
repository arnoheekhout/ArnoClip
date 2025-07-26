#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from http import server
import os
import logging
import argparse
import gradio as gr
from funasr import AutoModel
from videoclipper import VideoClipper
from llm.openrouter_api import openrouter_call, get_openrouter_models
from utils.trans_utils import extract_timestamps
from introduction import top_md_1, top_md_3, top_md_4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse testing')
    parser.add_argument('--lang', '-l', type=str, default = "en", help="language")
    parser.add_argument('--share', '-s', action='store_true', help="if to establish gradio share link")
    parser.add_argument('--port', '-p', type=int, default=7860, help='port number')
    parser.add_argument('--listen', action='store_true', help="if to listen to all hosts")
    args = parser.parse_args()
    
    if args.lang == 'zh':
        funasr_model = AutoModel(model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                                vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                                punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                                spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                                )
    else:
        funasr_model = AutoModel(model="iic/speech_paraformer_asr-en-16k-vocab4199-pytorch",
                                vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                                punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                                spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                                )
    audio_clipper = VideoClipper(funasr_model)
    audio_clipper.lang = args.lang
    
    server_name='127.0.0.1'
    if args.listen:
        server_name = '0.0.0.0'
        
        

    def audio_recog(audio_input, sd_switch, hotwords, output_dir):
        return audio_clipper.recog(audio_input, sd_switch, None, hotwords, output_dir=output_dir)

    def video_recog(video_input, sd_switch, hotwords, output_dir):
        return audio_clipper.video_recog(video_input, sd_switch, hotwords, output_dir=output_dir)

    def video_clip(dest_text, video_spk_input, start_ost, end_ost, state, output_dir):
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, dest_spk=video_spk_input, output_dir=output_dir
            )

    def mix_recog(video_input, audio_input, hotwords, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        audio_state, video_state = None, None
        if video_input is not None:
            res_text, res_srt, video_state = video_recog(
                video_input, 'No', hotwords, output_dir=output_dir)
            return res_text, res_srt, video_state, None
        if audio_input is not None:
            res_text, res_srt, audio_state = audio_recog(
                audio_input, 'No', hotwords, output_dir=output_dir)
            return res_text, res_srt, None, audio_state
    
    def mix_recog_speaker(video_input, audio_input, hotwords, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        audio_state, video_state = None, None
        if video_input is not None:
            res_text, res_srt, video_state = video_recog(
                video_input, 'Yes', hotwords, output_dir=output_dir)
            return res_text, res_srt, video_state, None
        if audio_input is not None:
            res_text, res_srt, audio_state = audio_recog(
                audio_input, 'Yes', hotwords, output_dir=output_dir)
            return res_text, res_srt, None, audio_state
    
    def mix_clip(dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, dest_spk=video_spk_input, output_dir=output_dir)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, dest_spk=video_spk_input, output_dir=output_dir)
            return None, (sr, res_audio), message, clip_srt
    
    def video_clip_addsub(dest_text, video_spk_input, start_ost, end_ost, state, output_dir, font_size, font_color):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, 
            font_size=font_size, font_color=font_color, 
            add_sub=True, dest_spk=video_spk_input, output_dir=output_dir
            )
            
    # UGLY SOLUTION
    def llm_inference_and_clip_subti(system_content, user_content, srt_text, model, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        llm_inference_and_clip(system_content, user_content, srt_text, model, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir, True)

    def llm_inference_and_clip(system_content, user_content, srt_text, model, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir, add_subtitles=False):
        # First, call the LLM
        llm_result = openrouter_call(model, user_content+'\n'+srt_text, system_content)
        
        # Then, clip based on the LLM result
        timestamp_list = extract_timestamps(llm_result)
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
            
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=add_subtitles)
            return llm_result, clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=add_subtitles)
            return llm_result, None, (sr, res_audio), message, clip_srt
        return llm_result, None, None, "No video or audio state found", ""
    
    def AI_clip(LLM_res, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        timestamp_list = extract_timestamps(LLM_res)
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=False)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=False)
            return None, (sr, res_audio), message, clip_srt
    
    def AI_clip_subti(LLM_res, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        timestamp_list = extract_timestamps(LLM_res)
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=True)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=True)
            return None, (sr, res_audio), message, clip_srt
    
    # gradio interface
    theme = gr.Theme.load("funclip/utils/theme.json")
    with gr.Blocks(theme=theme) as funclip_service:
        gr.Markdown(top_md_1)
        # gr.Markdown(top_md_2)
        gr.Markdown(top_md_3)
        gr.Markdown(top_md_4)
        video_state, audio_state = gr.State(), gr.State()
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    video_input = gr.Video(label="Video Input")
                    audio_input = gr.Audio(label="Audio Input")
                with gr.Column():
                    # with gr.Row():
                # video_sd_switch = gr.Radio(["No", "Yes"], label="👥Distinguish Speakers", value='No')
                    hotwords_input = gr.Textbox(label="🚒 Hotwords (Can be empty, multiple hotwords separated by spaces, Chinese hotwords only supported)")
                    output_dir = gr.Textbox(label="📁 File Output Dir (Can be empty, works stably on Linux and Mac systems)", value=" ")
                    with gr.Row():
                        recog_button = gr.Button("👂 ASR", variant="primary")
                        recog_button2 = gr.Button("👂👫 ASR+SD", variant="primary")
                video_text_output = gr.Textbox(label="✏️ Recognition Result")
                video_srt_output = gr.Textbox(label="📖 SRT Subtitles")
            with gr.Column():
                with gr.Tab("🧠 LLM Clipping"):
                    with gr.Column():
                        
                        prompt_head = gr.Textbox(
                            label="Prompt System (Modify as needed, but it's best not to change the main body and requirements)",
                            value="""You are a social media expert skilled at finding viral video moments using only subtitles (SRT). Given the SRT input, identify the most viral, shocking, rage-inducing, emotionally engaging, or interesting segments.
                                    Instructions:
                                    - For every 1 hour of video, extract ~15 strong segments.
                                    - Segments must be temporally continuous. Merge adjacent subtitles where appropriate to form coherent clips.
                                    - Ensure all timestamps are accurate and match the spoken text.
                                    - Output only in the format below:

                                    1. [Start Time - End Time] Text
                                    2. [Start Time - End Time] Text
                                    ...

                                    Use a dash (-) between timestamps. No extra text, commentary, or formatting outside the list.
                                  """
                        )
                        
                        prompt_head2 = gr.Textbox(label="Prompt User (No need to modify, will automatically concatenate the SRT subtitles from the bottom left)", value=("These are the video SRT subtitles to be clipped:"))
                        with gr.Column():
                            # Fetch free models from OpenRouter
                            free_models = get_openrouter_models()
                            model_choices = [model["id"] for model in free_models] if free_models else ["qwen/qwen3-235b-a22b-2507:free"]
                            
                            with gr.Row():
                                llm_model = gr.Dropdown(
                                    choices=model_choices,
                                    value=model_choices[0] if model_choices else "qwen/qwen3-235b-a22b-2507:free",
                                    label="LLM Model Name",
                                    allow_custom_value=True)
                            with gr.Row():
                                llm_clip_button = gr.Button("🧠 AI Clip Video", variant="primary")
                                llm_clip_subti_button = gr.Button("🧠 AI Clip Video+Subtitles", variant="primary")
                        llm_result = gr.Textbox(label="LLM Clipper Result")
                with gr.Tab("✂️ Text/Speaker Clipping"):
                    video_text_input = gr.Textbox(label="✏️ Text to Clip (Multiple segments connected with '#')")
                    video_spk_input = gr.Textbox(label="✏️ Speaker to Clip (Multiple speakers connected with '#')")
                    with gr.Row():
                        clip_button = gr.Button("✂️ Clip", variant="primary")
                        clip_subti_button = gr.Button("✂️ Clip+Subtitles", variant="primary")
                    with gr.Row():
                        video_start_ost = gr.Slider(minimum=-500, maximum=1000, value=0, step=50, label="⏪ Start Offset (ms)")
                        video_end_ost = gr.Slider(minimum=-500, maximum=1000, value=100, step=50, label="⏩ End Offset (ms)")
                with gr.Row():
                    font_size = gr.Slider(minimum=10, maximum=100, value=32, step=2, label="🔠 Subtitle Font Size")
                    font_color = gr.Radio(["black", "white", "green", "red"], label="🌈 Subtitle Color", value='white')
                    # font = gr.Radio(["Heiti", "Alibaba Sans"], label="Font")
                video_output = gr.Video(label="Video Clipped")
                audio_output = gr.Audio(label="Audio Clipped")
                clip_message = gr.Textbox(label="⚠️ Clipping Log")
                srt_clipped = gr.Textbox(label="📖 Clipped SRT Subtitles")            
                
        recog_button.click(mix_recog, 
                            inputs=[video_input, 
                                    audio_input, 
                                    hotwords_input, 
                                    output_dir,
                                    ], 
                            outputs=[video_text_output, video_srt_output, video_state, audio_state])
        recog_button2.click(mix_recog_speaker, 
                            inputs=[video_input, 
                                    audio_input, 
                                    hotwords_input, 
                                    output_dir,
                                    ], 
                            outputs=[video_text_output, video_srt_output, video_state, audio_state])
        clip_button.click(mix_clip, 
                           inputs=[video_text_input, 
                                   video_spk_input, 
                                   video_start_ost, 
                                   video_end_ost, 
                                   video_state, 
                                   audio_state, 
                                   output_dir
                                   ],
                           outputs=[video_output, audio_output, clip_message, srt_clipped])
        clip_subti_button.click(video_clip_addsub, 
                           inputs=[video_text_input, 
                                   video_spk_input, 
                                   video_start_ost, 
                                   video_end_ost, 
                                   video_state, 
                                   output_dir, 
                                   font_size, 
                                   font_color,
                                   ], 
                           outputs=[video_output, clip_message, srt_clipped])
        
        # fix the linting error
        llm_clip_button.click(llm_inference_and_clip, 
                           inputs=[prompt_head, 
                               prompt_head2, 
                               video_srt_output, 
                               llm_model, 
                               video_text_input, 
                               video_spk_input, 
                               video_start_ost, 
                               video_end_ost, 
                               video_state, 
                               audio_state, 
                               output_dir, 
                           ], 
                           outputs=[llm_result, video_output, audio_output, clip_message, srt_clipped])
        llm_clip_subti_button.click(
            llm_inference_and_clip_subti, 
            inputs=[
                prompt_head, 
                prompt_head2, 
                video_srt_output, 
                llm_model, 
                video_text_input, 
                video_spk_input, 
                video_start_ost, 
                video_end_ost, 
                video_state, 
                audio_state, 
                output_dir, 
            ], 
            outputs=[llm_result, video_output, audio_output, clip_message, srt_clipped])
    
    # start gradio service in local or share
    if args.listen:
        funclip_service.launch(share=args.share, server_port=args.port, server_name=server_name, inbrowser=False)
    else:
        funclip_service.launch(share=args.share, server_port=args.port, server_name=server_name)
