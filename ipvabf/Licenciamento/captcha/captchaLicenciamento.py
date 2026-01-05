from anticaptchaofficial.turnstileproxyless import *

solver = turnstileProxyless()
solver.set_verbose(1)
solver.set_key("174d6da17fc9ea20b644ed5b591ff5d9")
solver.set_website_url("https://internet.detrannet.mt.gov.br/ConsultaVeiculo.asp")
solver.set_website_key("0x4AAAAAAAO9omZCUc8pnQfN")

def anticaptcha():


    timeout = 120
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            token = solver.solve_and_return_solution()
            if token:
                return token
            else:
                print("Falha ao resolver CAPTCHA, tentando novamente...")
                time.sleep(3)
        except Exception as e:
            print("Erro ao tentar resolver CAPTCHA:", e)
            time.sleep(3)

    print("Tempo limite atingido")
    return None



if __name__ == "__main__":
    anticaptcha()