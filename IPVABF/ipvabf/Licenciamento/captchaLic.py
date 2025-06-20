import requests
import time
 
api_key = "CAP-1871290568179CFF2225BC9A45D3F3E2DF7092C54BCFC89C7C6487E0384E67B2"  # your api key of capsolver
site_key = "0x4AAAAAAAO9omZCUc8pnQfN"  # site key of your target site
site_url = "https://internet.detrannet.mt.gov.br/ConsultaVeiculo.asp"  # page url of your target site
 
def capsolver():
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url,
            "metadata": {
                "action": "" 
            }
        }
    }

    try:
        res = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=15)
        res.raise_for_status()
        resp = res.json()
    except Exception as e:
        print("Erro ao criar a tarefa:", e)
        return None

    #print("createTask response:", resp)

    if resp.get("errorId", 1) != 0 or "taskId" not in resp:
        print("Erro na criação da tarefa:", resp)
        return None

    task_id = resp["taskId"]
    #print(f"Tarefa criada: {task_id}, aguardando resultado...")

    timeout = 120
    start_time = time.time()

    while time.time() - start_time < timeout:
        time.sleep(3)  # Espera um pouco mais entre as chamadas
        try:
            res = requests.post("https://api.capsolver.com/getTaskResult", json={
                "clientKey": api_key,
                "taskId": task_id
            }, timeout=15)
            res.raise_for_status()
            resp = res.json()
        except Exception as e:
            print("Erro ao obter resultado da tarefa:", e)
            continue  # Tenta novamente

        #print("getTaskResult response:", resp)

        if resp.get("status") == "ready":
            return resp.get("solution", {}).get("token")

        elif resp.get("status") == "failed" or resp.get("errorId", 0) != 0:
            print("Erro ao resolver CAPTCHA:", resp)
            return None

    print("Tempo limite atingido")
    return None

token = capsolver()
print("Token resolvido")