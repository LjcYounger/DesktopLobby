try:
    from llama_cpp import Llama
except ImportError:
    print("ERROR: llama_cpp doesn't exist")
    
else:
    import time
    import os.path

    class AI:
        NAME="llama_cpp"
        PATH=""
        PUNCTUATIONS="!#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~！￥……（）【】、’‘”“；：。，？"

        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.json')
        with open(prompt_path, 'r', encoding='utf-8') as pj:
            PROMPT = pj.read()
        def __init__(self, inf_dict: dict):
            AI.NAME = inf_dict.get('NAME', 'llama_cpp')
            AI.PATH = inf_dict.get('PATH', f"AI/{AI.NAME}/qwen1_5-4b-chat-q4_k_m.gguf")
            try:  
                self.llm = Llama(
                    model_path=self.PATH,
                    n_ctx=4096,  # 上下文长度
                    n_threads=3,
                    seed=int(time.time()),
                    f16_kv=True,  # 使用半精度加速
                    verbose=False,
                )
            except Exception as e:
                self.llm=None
                print(f"[ERROR]AI Error: {e}")
        def init_char_prompt(self, system_prompt):
            self.llm.cache_prompt(self.llm.tokenize(system_prompt.encode('utf-8')))
        @staticmethod
        def generate_AI_prompt(name, introduction, hobby, emotions, example=""):
            prompt = AI.PROMPT.format(name=name, introduction=introduction, hobby=hobby, emotions=emotions, example=example)
            return prompt
        
        def _handle_answer(self, con0):
            chars=list(con0)
            if all(char in AI.PUNCTUATIONS for char in chars):
                return [con0]
            while chars and chars[0] in AI.PUNCTUATIONS:
                chars.pop(0)
            result=[]
            current_word=""

            for char in chars:
                if char in AI.PUNCTUATIONS:
                    current_word += char
                else:
                    if current_word:
                        result.append(current_word)
                    current_word=char
            if current_word:
                result.append(current_word)
            
            if len(result) < 8:
                return [''.join(result)]
            elif 8 <= len(result) < 16:
                part_len = len(result) // 2
                return [''.join(result[ :part_len]), ''.join(result[part_len: ])]
            else:
                con_len= len(result)
                part_len = con_len // 3
                return [''.join(result[ :part_len]),
                        ''.join(result[part_len: con_len-part_len]),
                        ''.join(result[con_len-part_len: ])]

        def get_answer_from_AI(self, history, system_prompt):
            """
            history: role, content
            cache=True -> cache prompt
            """
            output = self.llm.create_chat_completion(
                messages=[
                    {"role": "system","content": system_prompt},
                    *history
                ],
                max_tokens=1024,
                temperature=0.8,
                stop=["<|im_end|>"],
                repeat_penalty=1.1
            )
            total_tokens=output['usage']["total_tokens"]
            if output['choices']:
                choice=output["choices"][0]
                if 'message' in choice and 'content' in choice["message"]:
                    reply0=choice["message"]["content"]
                    print(f"[DEBUG]Reply: {reply0}")
                    try:
                        reply=reply0.split('#')
                        if reply0.startswith('#'):
                            emotion, content = reply[1], reply[2]
                        else:
                            content, emotion=reply[0], reply[1]
                        content_list=self._handle_answer(content)
                    except Exception:
                        content_list, emotion, total_tokens=self.get_answer_from_AI(history, system_prompt)
            return content_list, emotion, total_tokens
