import json
import os
import sys
from pathlib import Path


def setup_google_sheets():
    """Guia interativo para configurar Google Sheets."""
    print("=" * 60)
    print("  Configuração do Google Sheets para PyPizzas")
    print("=" * 60)
    print()
    print("Passo 1: Acesse https://console.cloud.google.com/")
    print("Passo 2: Crie um projeto ou selecione um existente")
    print("Passo 3: Ative as APIs:")
    print("   - Google Sheets API")
    print("   - Google Drive API")
    print()
    print("Passo 4: Crie uma Service Account:")
    print("   - IAM e Admin > Service Accounts > Criar")
    print("   - Nome: 'pypizzas-bot' (ou qualquer nome)")
    print("   - Papel: 'Editor' (ou 'Visualizador' se preferir)")
    print("   - Clique em 'Concluído'")
    print()
    print("Passo 5: Gere a chave JSON:")
    print("   - Clique na Service Account criada")
    print("   - Vá em 'Chaves' > 'Adicionar Chave' > 'JSON'")
    print("   - O arquivo será baixado automaticamente")
    print()

    current_dir = Path(__file__).parent
    credentials_path = current_dir / "credentials.json"

    if credentials_path.exists():
        try:
            with open(credentials_path) as f:
                creds = json.load(f)
            client_email = creds.get("client_email", "desconhecido")
            print(f"  ✅ credentials.json encontrado!")
            print(f"  📧 Email: {client_email}")
            print()
            print("Passo 6: Compartilhe sua planilha com este email:")
            print(f"   {client_email}")
            print("   (Role 'Editor' na planilha do Google Sheets)")
            print()
            print("Passo 7: Informe o nome da planilha no .env:")
            print("   GOOGLE_SHEETS_NAME=NomeDaSuaPlanilha")
            print()
            print("Pronto! O bot salvará pedidos automaticamente.")
            return True
        except json.JSONDecodeError:
            print("  ❌ credentials.json inválido. Baixe novamente.")
            return False

    print("  ❌ credentials.json não encontrado na raiz do projeto.")
    print()
    print("  Cole o arquivo JSON baixado como:")
    print(f"  {credentials_path}")
    print()
    return False


if __name__ == "__main__":
    setup_google_sheets()
