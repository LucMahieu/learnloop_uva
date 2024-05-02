import json

class JsonDataAccess:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def get_module_title(self):
        return self.data.get("module_name", "")

    def get_topics(self):
        return self.data.get("topics", [])

    def get_segments_for_topic(self, topic_index):
        topics = self.get_topics()
        if topic_index < len(topics):
            return topics[topic_index].get("segments", [])
        return []