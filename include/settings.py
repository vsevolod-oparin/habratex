import json

class Settings:

    key_habrasid = "habrasid"
    key_encoding = "encoding"
    key_formulas = "formulas"

    def __init__(self, filename):
        self.filename = filename
        self.settings = self.load() 

    def load(self):
        with open(self.filename, "r") as f:
            return json.loads(f.read())

    def save(self):
        with open(self.filename, "w") as f:
            f.write(json.dumps(self.settings))

    def habrasid(self):
        return self.settings[Settings.key_habrasid]

    def set_habrasid(self, habrasid):
        self.settings[Settings.key_habrasid] = habrasid
        self.save()

    def encoding(self):
        return self.settings[Settings.key_encoding]

    def set_encoding(self, encoding):
        self.settings[Settings.key_encoding] = encoding
        self.save()

    def formulas(self):
        return self.settings[Settings.key_formulas]

    def set_formulas(self, formulas):
        self.settings[Settings.key_formulas] = formulas
        self.save()        
