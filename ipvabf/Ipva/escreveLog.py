from datetime import datetime

data = datetime.now().isoformat(timespec='minutes').replace(":", "_")

def escreveLog(mensagemLog):
    with open(fr"C:\IpvaBf\IPVABF\ipvabf\Ipva\logIpva\log_execucao{data}.txt","a",encoding="utf-8") as log:
        log.write(datetime.now().isoformat(timespec='minutes').replace(":", "_")+": "+mensagemLog+"\n")

if __name__ == "__main__":
    escreveLog('')