import os
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import dropbox

def iniciar_extracao():
    hoje = datetime.today()
    mes = hoje.strftime("%m")
    ano = hoje.strftime("%Y")

    load_dotenv()
    LOGIN = os.getenv("SULA_EMAIL")
    SENHA = os.getenv("SULA_SENHA")
    DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

    options = Options()
    options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    })
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    dados_extraidos = []

    try:
        driver.get("https://corretor.sulamericaseguros.com.br")
        wait.until(EC.presence_of_element_located((By.NAME, "login"))).send_keys(LOGIN)
        wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(SENHA)
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"].g-recaptcha').click()
        print("🔐 Login realizado com sucesso.")
        wait.until(EC.url_contains("/area-logada"))

        driver.get("https://corretor.sulamericaseguros.com.br/area-logada/#/comissoes")

        campanhas = {
            "9512": "CIA SAÚDE",
            "6220": "SUASEG",
            "9598": "ODONTOLÓGICO SA",
            "1309": "SASEG"
        }

        for cod_campanha, nome_campanha in campanhas.items():
            try:
                print(f"\n➡️ Processando campanha: {nome_campanha} - {cod_campanha}")
                time.sleep(3)

                select_campanha = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Selecione a companhia']")))
                opcoes = select_campanha.find_elements(By.TAG_NAME, "option")
                valores = [opt.get_attribute("value") for opt in opcoes]

                if cod_campanha not in valores:
                    print(f"❌ Campanha {cod_campanha} não está disponível no momento.")
                    continue

                Select(select_campanha).select_by_value(cod_campanha)
                time.sleep(3)

                select_data = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Selecione uma data']")))
                datas_disponiveis = [
                    (opt.get_attribute("value"), opt.text.strip())
                    for opt in select_data.find_elements(By.TAG_NAME, "option")
                    if opt.get_attribute("value") != "0" and f"/{mes}/{ano}" in opt.text
                ]

                for valor, texto in datas_disponiveis:
                    print(f"🗓️ Data selecionada: {texto}")
                    Select(select_data).select_by_value(valor)
                    time.sleep(2)

                    botao_extrato = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @title='Gerar extrato']")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", botao_extrato)
                    driver.execute_script("arguments[0].click();", botao_extrato)
                    time.sleep(3)

                    try:
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "wrap-detalhamento")))
                        d_contents = driver.find_elements(By.CLASS_NAME, "d-content")

                        for content in d_contents:
                            info = {}
                            items = content.find_elements(By.CLASS_NAME, "d-item")
                            for item in items:
                                try:
                                    chave = item.find_element(By.TAG_NAME, "strong").text.strip().replace(":", "")
                                    valor = item.text.replace(item.find_element(By.TAG_NAME, "strong").text, "").strip()
                                    info[chave] = valor
                                except Exception:
                                    continue

                            if info:
                                percentual = info.get("Remuneração", "").strip().replace("%", "")
                                if percentual == "100":
                                    info["Tipo de Remuneração"] = "Agenciamento"
                                elif percentual == "2":
                                    info["Tipo de Remuneração"] = "Vitalício"
                                else:
                                    info["Tipo de Remuneração"] = "Outro"

                                info["Campanha"] = nome_campanha
                                info["Data Selecionada"] = texto
                                dados_extraidos.append(info)

                    except Exception as erro_cards:
                        print(f"⚠️ Erro ao carregar cards da data {texto}: {erro_cards}")
                        with open(f"erro_{cod_campanha}_{valor}.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)

            except Exception as erro_campanha:
                print(f"⚠️ Erro na campanha {cod_campanha}: {erro_campanha}")

        driver.quit()

        if dados_extraidos:
            nome_arquivo = f"extrato_sulamerica_{hoje.strftime('%Y-%m-%d')}.xlsx"
            df = pd.DataFrame(dados_extraidos)
            df.to_excel(nome_arquivo, index=False)
            print("✅ Extração concluída com sucesso.")

            # Enviar para Dropbox
            try:
                dbx = dropbox.Dropbox(DROPBOX_TOKEN)
                with open(nome_arquivo, "rb") as f:
                    dbx.files_upload(f.read(), f"/{nome_arquivo}", mode=dropbox.files.WriteMode("overwrite"))
                print("☁️ Arquivo enviado para o Dropbox com sucesso!")
            except Exception as erro_dropbox:
                print("⚠️ Erro ao enviar para o Dropbox:", erro_dropbox)

        else:
            print("⚠️ Nenhum dado encontrado para o período informado.")

    except Exception as e:
        print("❌ Erro geral:", e)
        driver.save_screenshot("erro_interface.png")
        driver.quit()

if __name__ == "__main__":
    iniciar_extracao()
