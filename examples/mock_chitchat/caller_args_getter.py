import datetime
import locale
import logging

from motto.agents.messages_processor import MessagesProcessor

from examples.mock_chitchat.inline_animations_prompt import generate_ia_prompt
import json

class CallerArgsGetter:
    def __init__(self, config, image_handler=None):
        self.log = logging.getLogger(__name__ + '.' + type(self).__name__)
        self.config = config
        self.model_name = config.get("chitchat.model_name")
        self.image_handler = image_handler
        if self.model_name not in ["gpt-4o-mini", "gpt-4o"]:
            raise Exception("Invalid mode")
        self.messages_processsor = MessagesProcessor(self.model_name, 5000, True)
        self.is_stream = True

    @property
    def situation_awareness(self):
        return self.config.get("chitchat_character.situation_awareness")

    @property
    def background(self):
        return self.config.get("chitchat_character.background")

    @property
    def timeout(self):
        return self.config.get("chitchat.timeout")

    @property
    def add_inline_animations(self):
        return self.config.get("chitchat.timeout")

    @property
    def permantent_response_direction(self):
        return self.config.get("chitchat_character.permanent_response_direction").strip()

    def insert_image(self, last_message):
        # NOTE: Currently the image is not counted in the token limit, so
        # keep the token cap in get_max_tokens() lower than the actual limit
        self.log.debug("Including image in messages")
        image_base64 = self.image_handler.get_image_base64()
        messages = []
        # Reformat text content to fit image format
        text_content = {
            "type": "text",
            "text": last_message}
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}",
                "detail": "low"}}
        new_message = {"role": "user",
                       "content": [text_content, image_content]}

        system_message = {"role": "system",
                          "content": "The images you are getting are coming from your vision sensors. Don't mention "
                                     "them unless necessary, and treat them not as images, but rather as what you see."}
        # Insert image in messages
        messages.append(system_message)
        messages.append(new_message)

        return messages

    def process_incoming_messages(self, history, direction=None):
        self.log.info("call process_incoming_messages")
        if not isinstance(history, list):
            history = [history]
        main_user = history[-1][0]
        if main_user == "robot":
            raise Exception("Invalid history")
        # remove all other users, replace main user with "user"
        messages = []
        for u, s, t in history:
            if u == main_user:
                messages.append(f"(user \"{s}\")")
            if u == "robot":
                messages.append(f"(assistant \"{s}\")")
        if direction is not None:
            messages.append(f"(system \"{direction}\")")
        return f'(Messages {"".join(messages)})'

    # @staticmethod
    # def iterator_token_by_token(response):
    #     for chunk in response:
    #         rez = chunk.choices[0].delta.content
    #         if rez != '' and rez is not None:
    #             yield rez

    def get_messages(self, history, direction):
        if (self.image_handler is None) or (self.image_handler.image is None):
            return "", self.process_incoming_messages(history, direction)
        if not isinstance(history, list):
            history = [history]
            # Add image if received
        if len(history) > 0 and isinstance(history[-1], tuple):
            processed_messages = "" if len(history) < 2 else self.process_incoming_messages(history[:-1])
            return self.insert_image(history[-1][1]),  processed_messages
        return "", self.process_incoming_messages(history)

    def get_caller_args(self, history, direction = None):
        self.log.info("call call_stream")
        full_sa = self.get_full_situation_awareness()
        if self.add_inline_animations:
            ia_prompt = generate_ia_prompt(self.config)
            full_system = self.background + "\n" + full_sa + "\n" + ia_prompt
        else:
            full_system = self.background + "\n" + full_sa

        if self.permantent_response_direction == "":
            full_direction = direction
        else:
            if direction is None:
                full_direction = self.permantent_response_direction
            else:
                full_direction = self.permantent_response_direction + "\n" + direction
        # todo I am not sure  about this trimmer
        history_messages = self.messages_processsor.cut_dialog_history(history)
        media_messages, messages = self.get_messages(history_messages, full_direction)

        return messages, [("system_msg", full_system, "String"),
                                              ("model_name", self.model_name, "String"),
                                              ("is_stream", self.is_stream, "Bool"),
                                ("media_msg", json.dumps(media_messages) if media_messages != "" else "", "String")]

    def get_full_situation_awareness(self):
        # set the locale to 'C' to ensure English is used
        locale.setlocale(locale.LC_TIME, 'C')
        now = datetime.datetime.now()
        return self.situation_awareness + " " + now.strftime("Today's date is %A, %B %d, %Y. Local time is %H:%M.")


