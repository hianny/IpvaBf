from anticaptchaofficial.turnstileproxyless import *

solver = turnstileProxyless()
solver.set_verbose(1)
solver.set_key("f28c1eadf668c9646d4b564e71678bc5")
solver.set_website_url("https://internet.detrannet.mt.gov.br/ConsultaVeiculo.asp")
solver.set_website_key("0x4AAAAAAAO9omZCUc8pnQfN")

def captchaChato():
    # Optionally specify page action value
    solver.set_action("checkout")

    # Optionally specify cData and chlPageData tokens for Cloudflare pages
    #solver.set_cdata("cdata_token")
    #solver.set_chlpagedata("chlpagedata_token")

    # Specify softId to earn 10% commission with your app.
    # Get your softId here: https://anti-captcha.com/clients/tools/devcenter
    solver.set_soft_id(0)

    token = solver.solve_and_return_solution()
    if token != 0:
        #print("token: "+token)
        print("token resolvido")
    else:
        print("task finished with error "+solver.error_code)

    return token
if __name__ == "__main__":
    captchaChato()