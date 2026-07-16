import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ["PORT"] = "5001"
from app import app
print("=" * 60)
print("Servidor rodando em http://localhost:5001")
print("Cardapio: http://localhost:5001/cardapio")
print("=" * 60)
app.run(host="0.0.0.0", port=5001, debug=False)
