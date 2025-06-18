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
                "action": ""  # pode ser removido se não usado
            }
        }
    }

    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    print("createTask response:", resp)

    task_id = resp.get("taskId")
    if not task_id:
        print("Falha ao criar tarefa:", res.text)
        return

    print(f"Tarefa criada: {task_id}, aguardando resultado...")

    timeout = 60
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(2)
        res = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        })
        resp = res.json()
        print("getTaskResult response:", resp)

        if resp.get("status") == "ready":
            return resp.get("solution", {}).get("token")
        elif resp.get("status") == "failed" or resp.get("errorId"):
            print("Erro ao resolver CAPTCHA:", resp)
            return

    print("Tempo limite atingido")
    return

token = capsolver()
print("Token resolvido:", token)

