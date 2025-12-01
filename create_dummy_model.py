import pickle
from ml_model import DummyModel

# Create and pickle the dummy model
model = DummyModel()
with open('book_genre_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Dummy model 'book_genre_model.pkl' created successfully with the correct module path.")
