# Dockerfile para aplicação FastAPI com Oracle Instant Client e agendador de tarefas

# Author: Gustavo F. Lima
# License: MIT
# Created: 2025

# Imagem base Python oficial (versão slim para reduzir tamanho e melhorar a segurança)
FROM python:3.13-slim 

# Instala dependências do sistema necessárias para:
# - Oracle Instant Client
# - Segurança (certificados)
# - Diagnóstico e gerenciamento de processos
# - Fuso horário
RUN apt-get update && apt-get install -y \
    libaio1t64 \
    libnsl2 \
    libgssapi-krb5-2 \
    unzip \
    wget \
    ca-certificates \
    procps \
    tzdata \
    # Cria link simbólico esperado por algumas libs Oracle
    && ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1 \
    # Limpa cache do apt para reduzir o tamanho da imagem
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho da aplicação
WORKDIR /app

# Configurações de ambiente para Python:
# - Evita criação de arquivos .pyc
# - Força saída imediata no stdout/stderr (ideal para logs)
# - Define fuso horário padrão da aplicação
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Sao_Paulo

# Aplica o fuso horário no sistema operacional
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Instala o Oracle Instant Client (necessário para conexões Oracle)
RUN mkdir -p /opt/oracle \
 && cd /opt/oracle \
 && wget https://download.oracle.com/otn_software/linux/instantclient/2326000/instantclient-basic-linux.x64-23.26.0.0.0.zip \
 && unzip instantclient-basic-linux.x64-23.26.0.0.0.zip \
 && rm instantclient-basic-linux.x64-23.26.0.0.0.zip

# Variáveis de ambiente do Oracle Client
ENV ORACLE_HOME=/opt/oracle/instantclient_23_26
ENV LD_LIBRARY_PATH=$ORACLE_HOME
ENV PATH=$ORACLE_HOME:$PATH

# Copia o arquivo de dependências
COPY requirements.txt .

# Atualiza o pip e instala dependências Python
# --no-cache-dir evita cache e reduz o tamanho final da imagem
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para o container
COPY . .

# Expõe a porta usada pela API FastAPI
EXPOSE 8000

# Inicializa:
# - Scheduler em background
# - API FastAPI via Uvicorn como processo principal
CMD ["sh", "-c", "python scheduler/scheduler.py & exec uvicorn app.api:app --host 0.0.0.0 --port 8000"]

