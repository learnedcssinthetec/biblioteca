class DummyModel:
    def predict(self, data):
        age = data[0][0]
        if age < 12:
            return ["Libro Infantil"]
        elif 12 <= age <= 18:
            return ["Literatura Juvenil"]
        elif 19 <= age <= 25:
            return ["Fantasía"]
        elif 26 <= age <= 40:
            return ["Ciencia Ficción"]
        elif 41 <= age <= 60:
            return ["Misterio"]
        else:
            return ["No Ficción"]
