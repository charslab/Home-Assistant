[![license](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://github.com/charslab/Home-Assistant/blob/master/LICENSE)

# Home Assistant

Home assistant inspired by Amazon Echo, based on wit.ai with speech/intent recognition

## Quickstart

### Setup

Clone the repository with

    git clone https://github.com/charslab/Home-Assistant.git 

Before you can get started you'll have to configure a few things.

- Install all python requirements with 

      pip3 install -r requirements.txt

- Install snowboy:
    - You can download a binary distribution of [snowboy](https://github.com/Kitt-AI/snowboy#precompiled-binaries-with-python-demo) (you'll only need \_snowboydetect.so, put in the the project's main folder), or
    - Compile everything from scratch: just run
        ```
        git submodule init
        git submodule update
        ./ubuntu_setup.sh
        ```


- Create a new [Wit.ai](https://wit.ai) project. 
- In **auth.py**:
    - Set **WIT_KEY** - with your Wit project key.
    - Set **YANDEX_KEY** - [Register here](https://translate.yandex.com/developers) to obtain a free Yandex key.
    - Set **GOOGLE_KNOWLEDGE_KEY** - [Follow this guide](https://developers.google.com/maps/documentation/embed/get-api-key) to obtain a free Google APIs key, for Knowledge service.
    - Set **WOLFRAM_ALPHA_KEY** - [Register here](https://developer.wolframalpha.com/portal/apisignup.html), to obtain a free Wolfram Alpha key.
    
### Adding intents

After setting up your wit.ai application backend (see https://wit.ai/docs/quickstart), you can add intents callbacks for the HomeAssistant class.

For example, let's say you have an intent named "weather_forecast" in your wit.ai app. 
In homeassistant.py you have to add: 
    
```python
@intent
def weather_forecast(self, entities):
  # handle weather forecast request
```

See [homeassistant.py](https://github.com/charslab/Home-Assistant/blob/master/homeassistant.py) for more examples.

**Important:** a callback's name *must exactly match* its intent's name (set in wit.ai)

### Running

You can start Home-Assistant with 

    python3 main.py
    
If you plan to run it on embedded devices or single board computers, we reccomend to compile the entire application to binary to gain a performance improvement.
For compiling, you have to install **nuitka**.
You can do that with:

    sudo apt install nuitka
    
Then run 

    ./compile.sh
    
*Make sure that --python-version in compile.sh matches your current python version (i.e 3.4, 3.5..)*


## Contributing

You are free to open pull requests, we'd appreciate it. 
Make sure to follow the same coding conventions that we are using. 

Things you may want to focus on in your contributions:
- Better support for internationalization/localization
      
