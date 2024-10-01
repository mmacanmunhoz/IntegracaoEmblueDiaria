
import json

def carregar_credenciais():
    with open('data/credenciais.json') as f:
        return json.load(f)
    
def credencial(nome):
    with open('data/credenciais.json') as f:
        return json.load(f)[nome]