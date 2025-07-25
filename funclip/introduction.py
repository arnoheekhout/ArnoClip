top_md_1 = ("""
    <div align="center">
    <div style="display:flex; gap: 0.25rem;" align="center">
    FunClip: <a href='https://github.com/alibaba-damo-academy/FunClip'><img src='https://img.shields.io/badge/Github-Code-blue'></a> 
    🌟Support us: <a href='https://github.com/alibaba-damo-academy/FunClip/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunClip.svg?style=social'></a>
    </div>
    </div>
    
    Based on Alibaba Tongyi Lab's self-developed and open-sourced [FunASR](https://github.com/alibaba-damo-academy/FunASR) toolkit and Paraformer series models for speech recognition, endpoint detection, punctuation prediction, timestamp prediction, speaker diarization, and hotword customization open-source pipeline

    Accurate recognition, freely copy the desired paragraphs, or set speaker identifiers, one-click clipping and subtitle addition

    * Step1: Upload video or audio files (or use the examples below), click the **<font color="#f7802b">Recognize</font>** button
    * Step2: Copy the required text from the recognition results to the upper right, or set the speaker identifier, set offsets and subtitle configuration (optional)
    * Step3: Click the **<font color="#f7802b">Clip</font>** button or **<font color="#f7802b">Clip and Generate Subtitles</font>** button to get results
    
    🔥 FunClip now integrates large language model intelligent editing function, choose an LLM model to experience~
    """)

top_md_3 = ("""Visiting the FunASR project and paper can help you gain in-depth understanding of the speech processing models used in ParaClipper:
    <div align="center">
    <div style="display:flex; gap: 0.25rem;" align="center">
        FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR'><img src='https://img.shields.io/badge/Github-Code-blue'></a> 
        FunASR Paper: <a href="https://arxiv.org/abs/2305.11013"><img src="https://img.shields.io/badge/Arxiv-2305.11013-orange"></a> 
        🌟Star FunASR: <a href='https://github.com/alibaba-damo-academy/FunASR/stargazers'><img src='https://img.shields.io/github/stars/alibaba-damo-academy/FunASR.svg?style=social'></a>
    </div>
    </div>
    """)

top_md_4 = ("""We provide three LLM calling methods in the 'LLM Intelligent Clipping' module,
            1. Select Alibaba Cloud Bailian platform to call qwen series models via API, which requires you to prepare an API key from the Bailian platform. Please visit [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/#/home);
            2. Selecting models starting with GPT means calling the official OpenAI API, which requires you to prepare your own secret key and network environment;
            3. The [gpt4free](https://github.com/xtekky/gpt4free?tab=readme-ov-file) project is also integrated into FunClip, allowing you to call GPT models for free through it;
            
            Methods 1 and 2 require entering the corresponding API key in the interface        
            Method 3 may be very unstable, with long return times or failed result acquisition. You can try multiple times or prepare your own secret key to use methods 1 and 2
            
            Do not open multiple interfaces on the same port simultaneously, as this will cause file uploads to be very slow or freeze. Simply close other interfaces to resolve this issue
            """)
