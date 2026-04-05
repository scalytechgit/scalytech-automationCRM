from services.automation import processar_leads
import time

if __name__ == "__main__":
    while True:
        print("Rodando automação...")
        processar_leads()
        print("Aguardando 24h...\n")
        time.sleep(86400)  # roda todo dia