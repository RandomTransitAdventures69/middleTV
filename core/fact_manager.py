import json
import random

from pathlib import Path


class FactManager:

    def __init__(self):

        self.base = (
            Path(__file__)
            .resolve()
            .parent.parent
        )

        self.config_file = (
            self.base
            / "config"
            / "facts.json"
        )

        self.config_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.data = self.load()


    def load(self):

        if not self.config_file.exists():

            data = {
                "facts": []
            }

            self.save(data)

            return data


        try:

            with open(
                self.config_file,
                "r"
            ) as f:

                return json.load(f)

        except (
            json.JSONDecodeError,
            OSError
        ):

            return {
                "facts": []
            }


    def save(self, data=None):

        if data is not None:

            self.data = data


        with open(
            self.config_file,
            "w"
        ) as f:

            json.dump(
                self.data,
                f,
                indent=4
            )


    def get_random_fact(self):

        facts = self.data.get(
            "facts",
            []
        )


        available = [
            fact
            for fact in facts
            if fact.get(
                "enabled",
                True
            )
            and fact.get(
                "text",
                ""
            ).strip()
        ]


        if not available:

            return None


        return random.choice(
            available
        )


    def add_fact(
        self,
        text,
        category="custom"
    ):

        text = text.strip()


        if not text:

            return False


        self.data.setdefault(
            "facts",
            []
        )


        self.data["facts"].append(
            {
                "text": text,
                "category": category,
                "enabled": True
            }
        )


        self.save()

        return True