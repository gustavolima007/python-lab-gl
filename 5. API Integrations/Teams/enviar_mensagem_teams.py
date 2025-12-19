"""
Este script envia uma mensagem de alerta para um grupo do Microsoft Teams
utilizando um fluxo do Power Automate como endpoint HTTP.

O fluxo recebe os dados em formato JSON e publica a mensagem automaticamente
no canal configurado do Teams. Ideal para alertas de falhas, erros de processos
ou notificações automáticas de sistemas.
"""

import requests

# URL do fluxo do Power Automate (deve ser fornecida via variável de ambiente ou secret)
POWER_AUTOMATE_URL = "##################################"

# Dados do alerta a ser enviado
alerta = {
    "alerta": "🚨 Alerta automático: processo de contratos falhou!",
    "detalhes": "Erro na importação de dados. Verificar logs do servidor."
}

headers = {
    "Content-Type": "application/json"
}

print("📤 Enviando alerta ao Power Automate...")
response = requests.post(POWER_AUTOMATE_URL, json=alerta, headers=headers)

print(f"📡 Status: {response.status_code}")
if response.status_code in (200, 202):
    print("✅ Alerta enviado com sucesso para o Teams!")
else:
    print("❌ Erro ao enviar alerta:")
    print(response.text)
