"""Telegram Scraper Class to Get data of public groups"""
import datetime
import json
import pytz
from telethon import TelegramClient
from telethon import functions

API_ID = 16021392  # telegram id
API_HASH = "c7719a1ae53cc7fc76501f4da6ed907b"  # telegram hash


class Telegram:
    """Telegram Scraping Class"""

    def get_messages(self, group_id):
        """Method to get the messages"""
        for message in self.client.iter_messages(group_id, offset_date=self.to_date):
            if self.from_date < message.date.replace(tzinfo=self.utc):
                data_dict = {"keyword": "covid19",
                             "group_id": group_id,
                             "message_id": message.id,
                             "date": str(message.date),
                             "message": str(message.text)}
                self.all_data["data"].append(data_dict)
                print(message.id, ":", message.date, ':', message.text)
            else:
                break
        print(self.all_data)
        with open('covid19.json', 'w', encoding='utf-8') as output_file:
            json.dump(self.all_data, output_file, indent=4, ensure_ascii=False)

    async def search_keywords(self):
        result = await self.client(functions.contacts.SearchRequest(q="covid19", limit=100))
        # print(result.stringify())
        # print(result.to_dict()["results"])
        for channel in result.to_dict()["results"]:
            try:
                self.channel_ids.append(channel["channel_id"])
            except Exception as keyword_error:
                print(keyword_error)

    def __init__(self):
        self.utc = pytz.UTC
        self.group_name = "MyGovCoronaNewsdesk"  # Name of telegram group
        self.client = TelegramClient('scraping_session', API_ID, API_HASH).start()
        self.all_data = {
            "data": []
        }
        self.channel_ids = []
        self.to_date = datetime.date(2020, 4, 12)  # date from until when we need data
        # starting date from when we need data
        self.from_date = datetime.datetime(2020, 4, 1).replace(tzinfo=self.utc)
        print("Object Initialized")
        with self.client:
            self.client.loop.run_until_complete(self.search_keywords())


if __name__ == "__main__":
    obj = Telegram()
    # iterating over searched keywords
    with obj.client:
        for channel_id in obj.channel_ids:
            obj.get_messages(channel_id)
