import tiktoken
def get_max_tokens(model_name):
    if model_name == "gpt-3.5-turbo":
        return 10000  # real limit 16385
    if model_name == "gpt-4-turbo-preview":
        return 10000  # Limit max number of tokens to reduce cost (real limit 128000)
    if model_name == "gpt-4o" or model_name == "gpt-4-turbo":
        return 10000  # Set max number of tokens to reduce cost (real limit 128000)
    raise Exception("Unknown model name")


class HistoryProcessor:

    def __init__(self, model_name,  max_response_tokens):
        self.model_name = model_name
        self.max_tokens = get_max_tokens(self.model_name) -  max_response_tokens
        # we need tokenizer only to calculate number of tokens and cut dialog history if needed
        self.encoder = tiktoken.encoding_for_model(self.model_name)

    def num_tokens_for_single_message(self, m):
        # will work for all models except outdated gpt-3.5-turbo-0301
        tokens_per_message = 3  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        # tokens_per_name = 1  # if there's a name, the role is omitted
        num_tokens = tokens_per_message
        for key, value in m.items():
            num_tokens += len(self.encoder.encode(value))
            # if key == "name":
            #     num_tokens += tokens_per_name
        return num_tokens

    def process_dialog_history(self, messages):

        # remove old history in order to fit into the prompt
        lines_tokens = [self.num_tokens_for_single_message(m) for m in messages]
        sum_tokens = 0
        i_cut = 0
        for i in reversed(range(len(lines_tokens))):
            sum_tokens += lines_tokens[i]
            if sum_tokens > self.max_tokens:
                i_cut = i + 1
                break
        if i_cut > 0:
            messages = messages[i_cut:]
        return messages
