import requests
import json


class TranslatorBot(object):
    def __init__(self):
        self.keys = self._readAPIKey()

    def _readLastUpdate(self, source_lang, target_lang):
        try:
            with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'r') as f:
                number = f.read()

            return int(number)

        except:
            self._writeUpdate(source_lang, target_lang, 0)
            return 0

    def _readAPIKey(self):
        with open('apikey.json', 'r') as f:
            keys = json.load(f)
        return keys

    def _writeUpdate(self, source_lang, target_lang, number):
        with open('lastUpdate{}{}.txt'.format(source_lang, target_lang), 'w') as f:
            f.write(str(number))

    def _crawlUpdate(self, api_endpoint, offset):
        payload = {"offset": offset}
        resp = requests.post(api_endpoint, data=payload)
        data = resp.json()
        return data['result']

    def _get_lang_id(self, lang):
        lang_table = {
                "ko": 1
              , "en": 2
              , "zh": 4
              , "th": 6
              , "ja": 8
              , "es": 9
              , "pt": 10
              , "vi": 11
              , "de": 12
              , "fr": 13
                }
        return lang_table.get(lang)

    def _get_mail(self):
        with open('getMail.txt', 'r') as f:
            data_raw = f.read()
            data = data_raw.split(',')

        return data[0].strip(), data[1].strip()

    def _translate(self, source_lang, target_lang, sentence, memo):
        endpoint = "https://translator.ciceron.me/translate"
        source_lang_id = self._get_lang_id(source_lang)
        target_lang_id = self._get_lang_id(target_lang)
        payload = {
                    "source_lang_id": source_lang_id
                  , "target_lang_id": target_lang_id
                  , "sentence": sentence
                  , "where": "api"
                  , "memo": memo
                }
        key, value = self._get_mail()
        payload[key] = value
        if source_lang_id != None and target_lang_id != None:
            try:
                resp = requests.post(endpoint, data=payload, timeout=10, verify=False)
                data = resp.json() if resp.status_code == 200 else {"ciceron":"Not enough servers. Investment is required.", 'google':""}

            except:
                data = {"ciceron":"Not enough servers. Investment is required.", 'google':""}

            result_ciceron = data.get('ciceron')
            result_google = data.get('google')
            if source_lang in ["en", "ko"] and target_lang in ["en", "ko"]:
                message = "Langchain Translation bot is unified into one account!\nhttp://t.me/langchainbot\n\nLangChain:\n{}\n\nGoogle:\n{}\n\nPowered by LangChain".format(result_ciceron, result_google)
            else:
                message = "{}\n\nPowered by LangChain\nUsage: ![Source language][Target language] [Sentence]\nKorean-ko, English-en, Japanese-ja, Chinese-zh".format(result_google)

        else:
            message = "Oops! wrong language code seems to be inserted!\nPlease check the usage!\n\nUsage: ![Source language][Target language] [Sentence]\nKorean-ko, English-en, Japanese-ja, Chinese-zh"

        return message

    def _sendMessage(self, api_endpoint, chat_id, message_id, message):
        payload = {
                      "chat_id": chat_id
                    , "text": message
                    , "reply_to_message_id": message_id
                  }

        for _ in range(100):
            resp = requests.post(api_endpoint, data=payload, timeout=5)
            if resp.status_code == 200:
                break

        else:
            print("Telegram deadlock")

    def _main(self, source_lang, target_lang, apiKey, wakeup_key):
        apiEndpoint_update = "https://api.telegram.org/bot{}/getUpdates".format(apiKey)
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(apiKey)

        lastnumber = self._readLastUpdate(source_lang, target_lang)
        res = self._crawlUpdate(apiEndpoint_update, lastnumber+1)

        update_id = lastnumber
        for item in res:
            if item['update_id'] < lastnumber:
                continue

            update_id = max(update_id, item['update_id'])
            whole_message = item.get('message')
            if whole_message is None:
                continue

            chat_id = item['message']['chat']['id']
            message_id = item['message']['message_id']
            text_before = item['message'].get('text')
            user_name = item['message'].get('from').get('username')
            chat_type = item['message']['chat']['type']
            group_title = item['message']['chat'].get('title')
            if text_before is None:
                continue
            else:
                text_before = text_before.strip()

            if text_before.startswith(wakeup_key):
                text_before = text_before.replace(wakeup_key, '').strip()
                print(text_before)
                message = self._translate(source_lang, target_lang, text_before, "Telegram:{}|{}|{}".format(user_name, chat_type, group_title))
                print(message)
                self._sendMessage(apiEndpoint_send, chat_id, message_id, message)

        self._writeUpdate(source_lang, target_lang, update_id)

    def _generalMain(self, apiKey, wakeup_key):
        apiEndpoint_update = "https://api.telegram.org/bot{}/getUpdates".format(apiKey)
        apiEndpoint_send = "https://api.telegram.org/bot{}/sendMessage".format(apiKey)

        lastnumber = self._readLastUpdate("ge", "ge")
        res = self._crawlUpdate(apiEndpoint_update, lastnumber+1)

        update_id = lastnumber
        source_lang = ""
        target_lang = ""

        for item in res:
            if item['update_id'] < lastnumber:
                continue

            update_id = max(update_id, item['update_id'])
            whole_message = item.get('message')
            if whole_message is None:
                continue

            chat_id = item['message']['chat']['id']
            message_id = item['message']['message_id']
            text_before = item['message'].get('text')
            user_name = item['message'].get('from').get('username')
            chat_type = item['message']['chat']['type']
            group_title = item['message']['chat'].get('title')
            if text_before is None:
                continue
            else:
                text_before = text_before.strip()

            if text_before.startswith(wakeup_key):
                language_pair = text_before[:5]
                source_lang = language_pair[1:3]
                target_lang = language_pair[3:5]

                text_before = text_before.replace(language_pair, '').strip()
                print(text_before)
                message = self._translate(source_lang, target_lang, text_before, "Telegram:{}|{}|{}".format(user_name, chat_type, group_title))
                print(message)
                self._sendMessage(apiEndpoint_send, chat_id, message_id, message)

        self._writeUpdate("ge", "ge", update_id)

    def koEnTranslation(self):
        self._main('ko', 'en', self.keys['koen'], '!koen')

    def enKoTranslation(self):
        self._main('en', 'ko', self.keys['enko'], '!enko')

    def generalTranslation(self):
        self._generalMain(self.keys['gege'], '!')


if __name__ == "__main__":
    translator = TranslatorBot()
    translator.koEnTranslation()
