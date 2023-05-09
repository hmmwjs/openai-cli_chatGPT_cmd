import datetime
import os
import json
import argparse 
from colorama import init, Fore, Back, Style
import openai

class Chatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.file_name = None
        self.messages = []
        self.chat_response = ""

    def connect_to_api(self):
        openai.api_key = self.api_key
        max_try_num = 1
        while(max_try_num > 0):
            try:
                model_list = openai.Model.list()
                i = 0
                for mi in model_list.data:
                    if "gpt" in mi.root:
                        i += 1
                        print(f"GPT model {i}: {mi.root}")
            except:
                print(Fore.YELLOW + f"Net error, left try times: {max_try_num}")
                max_try_num -= 1
                continue
            break
        if(max_try_num <= 0):
            print(Fore.RED + "Check Network!")
            exit()
        else:
            print(Fore.GREEN + "Connected.")

    def create_log_file(self):
        current_time = datetime.datetime.now()
        self.file_name = os.path.join(".", "record", f"{current_time.strftime('%Y%m%d_%H%M%S')}.md")
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        print(Fore.GREEN + self.file_name)

    def write_readble_to_txt(self, role, content_str):
        role_color={"system":"red","user":"blue","assistant":"green"}
        with open(self.file_name, "a") as f:
            f.write(f"## <font color=\"{role_color[role]}\">{role}:</font>\n{content_str}\n\n")

    def read_from_txt(self, filename):
        restored_list = []
        with open(filename, "r") as f:
            cur_str_all = f.readlines()
            for cur_str0 in cur_str_all:
                cur_str = cur_str0.strip()
                try:
                    cur_msg = eval(cur_str)
                    if isinstance(cur_msg, dict):
                        restored_list.append(cur_msg)
                except ValueError:
                    print("Invalid string:", cur_str)
        return restored_list

    def initialize(self):
        init() # color font
        self.connect_to_api()
        self.create_log_file()
        self.messages.append({"role": "system", "content": "你的每次回答除了必要的代码，不能有任何的解释和说明"})
        print_message(self.messages)
        self.write_readble_to_txt(self.messages[-1]["role"], self.messages[-1]["content"])

    def get_user_input(self):
        content = input(Fore.LIGHTYELLOW_EX +"User: ")
        self.messages.append({"role": "user", "content": content})
        self.write_readble_to_txt(self.messages[-1]["role"], self.messages[-1]["content"])

    def generate_chat_response(self):
        print(Fore.GREEN +f'ChatGPT:')
        for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=0,
            stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                print(content, end='',flush=True)
                self.chat_response += content
        print("")
        self.messages.append({"role": "assistant", "content": self.chat_response})
        self.write_readble_to_txt(self.messages[-1]["role"], self.messages[-1]["content"])

    def run_chatbot(self):
        while True:
            self.get_user_input()
            self.generate_chat_response()

def print_message(msg):
    role_color = {"system": Fore.RED, "user": Fore.LIGHTYELLOW_EX, "assistant": Fore.GREEN}
    for mi in msg:
        print(role_color[mi["role"]] + f"{mi['role']}: {mi['content']}")

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set!")
    chatbot = Chatbot(api_key)
    chatbot.initialize()
    chatbot.run_chatbot()

if __name__ == '__main__':
    main()
