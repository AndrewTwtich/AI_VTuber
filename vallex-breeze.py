from utils.generation import preload_models, generate_audio_from_long_text, SAMPLE_RATE
from scipy.io.wavfile import write as write_wav
from openai import OpenAI
import os
import os.path
import winsound
import socket

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'andrew_livestream'
token = 'oauth:whk7u4rfqq6fljsf9madjs43hukn8u'
channel = '#andrew_livestream'

# download and load all models
preload_models()

sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))
sock.recv(2048).decode('utf-8')
sock.recv(2048).decode('utf-8')


def converting(text):
    if os.path.isfile('/outputs.wav'):
        os.remove('/outputs.wav')
    audio = generate_audio_from_long_text(text, prompt="bronya")
    write_wav("outputs.wav", SAMPLE_RATE, audio)
    winsound.PlaySound('/outputs.wav', winsound.SND_ALIAS)
    winsound.PlaySound(None, winsound.SND_ALIAS)

# Chat with an intelligent assistant in your terminal


# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

history = [
    {"role": "system", "content": "你是一位虛擬實況主。你的目的是主持一個線上直播並且與觀看的人互動、聊天或是玩遊戲，你只能使用利用繁體中文回答，請用友善、口語化的語氣互動"},
    {"role": "user", "content": "請自我介紹"},
]

while True:
    completion = client.chat.completions.create(
        model="YC-Chen/Breeze-7B-Instruct-v1_0-GGUF",
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content

    print()
    history.append(new_message)
    converting(new_message["content"])
    
    print()
    resp = sock.recv(2048).decode('utf-8')
    i = 29+(len(channel)-1)*4
    text_resp = ""
    while i < len(resp):
        text_resp += (resp[i])
        i += 1
        if resp[i] == '\r':
            break

    history.append({"role": "user", "content": text_resp})
