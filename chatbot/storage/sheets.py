import logging
from typing import Optional
from config import settings
from models import DadosPedido

logger = logging.getLogger(__name__)


def registrar_pedido_google_sheets(dados: DadosPedido) -> bool:
    """Salva pedido no Google Sheets."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(
            settings.google_credentials_path, scopes=scopes
        )
        gc = gspread.authorize(creds)
        spreadsheet = gc.open(settings.google_sheets_name)
        worksheet = spreadsheet.sheet1
        
        all_values = worksheet.get_all_values()
        is_new_sheet = len(all_values) == 0
        
        if is_new_sheet:
            cabecalho = ["Nº Pedido (Dia)", "Data", "Hora", "Itens", "Total (R$)", 
                        "Lucro (R$)", "Pagamento", "Endereço", "Observações"]
            worksheet.append_row(cabecalho)
        
        itens_formatados = ", ".join([
            f"{item.quantidade}x {item.sabor} ({item.tamanho.value})" 
            for item in dados.itens
        ])
        
        nova_linha = [
            dados.numero_do_dia,
            dados.timestamp.strftime("%d/%m/%Y"),
            dados.timestamp.strftime("%H:%M:%S"),
            itens_formatados,
            dados.total,
            dados.lucro,
            dados.pagamento.value,
            dados.endereco,
            dados.observacoes
        ]
        
        worksheet.append_row(nova_linha)
        nova_linha_numero = len(worksheet.get_all_values())
        
        _formatar_linha(worksheet, spreadsheet, nova_linha_numero, is_new_sheet)
        
        logger.info(f"Pedido #{dados.numero_do_dia} salvo no Google Sheets")
        return True
        
    except FileNotFoundError:
        logger.warning(f"Arquivo de credenciais não encontrado: {settings.google_credentials_path}")
        return False
    except Exception as e:
        logger.error(f"Erro ao salvar no Google Sheets: {e}")
        return False


def _formatar_linha(worksheet, spreadsheet, linha_numero: int, is_new_sheet: bool):
    """Aplica formatação na linha do pedido."""
    try:
        cor_verde_agua = {"red": 0.85, "green": 0.96, "blue": 0.93}
        borda_solida = {"style": "SOLID", "width": 1, "color": {"red": 0.7, "green": 0.7, "blue": 0.7}}
        
        requests = []
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": linha_numero - 1,
                    "endRowIndex": linha_numero
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": cor_verde_agua,
                        "borders": {
                            "top": borda_solida, "bottom": borda_solida,
                            "left": borda_solida, "right": borda_solida
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,borders)"
            }
        })
        
        if is_new_sheet:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": worksheet.id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.49, "green": 0.75, "blue": 0.65},
                            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                            "borders": {"top": borda_solida, "bottom": borda_solida, "left": borda_solida, "right": borda_solida}
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,borders)"
                }
            })
            colunas_largura = [
                {"range": {"sheetId": worksheet.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 350}},
                {"range": {"sheetId": worksheet.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 6}, "properties": {"pixelSize": 120}},
                {"range": {"sheetId": worksheet.id, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 8}, "properties": {"pixelSize": 400}},
                {"range": {"sheetId": worksheet.id, "dimension": "COLUMNS", "startIndex": 8, "endIndex": 9}, "properties": {"pixelSize": 250}}
            ]
            for col in colunas_largura:
                requests.append({"updateDimensionProperties": {**col, "fields": "pixelSize"}})
        
        if requests:
            spreadsheet.batch_update({"requests": requests})
        
        worksheet.format(f'E{linha_numero}:F{linha_numero}', 
                        {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}})
        
    except Exception as e:
        logger.warning(f"Erro ao formatar planilha (não crítico): {e}")