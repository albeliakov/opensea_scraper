from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from time import sleep
import json
from datetime import datetime, timezone
from dotenv import dotenv_values
from web3 import Web3, EthereumTesterProvider

import chromedriver_autoinstaller
chromedriver_autoinstaller.install()


targetURL = "https://opensea.io/assets/ethereum/0x495f947276749ce646f68ac8c248420045cb7b5e/103408158708217304912328131381952067473052097855567303395336337378376880751092"
# targetURL = "https://opensea.io/assets/ethereum/0x86825dfca7a6224cfbd2da48e85df2fc3aa7c4b1/1"
# targetURL = "https://opensea.io/assets/solana/FuAA4x3MLRXTYj9jCsKugufUz6UbSDYur1RAfs7rsKxS"
# targetURL = "https://opensea.io/assets/ethereum/0x5cc5b05a8a13e3fbdb0bb9fccd98d38e50f90c38/34871"


def botInitialization():
    # Initialize the Bot
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    # driver.execute_script("window.open()")
    # driver.implicitly_wait(20)
    return driver


def get_time_from_etherscan(tx: str):
    INFURA_API_KEY = config = dotenv_values(".env")["INFURA_API_KEY"]
    provider_url = "https://mainnet.infura.io/v3/{0}".format(INFURA_API_KEY)

    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.isConnected():
        return

    bn = w3.eth.getTransaction(tx).blockNumber
    ts = w3.eth.getBlock(bn).timestamp
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


driver = botInitialization()

driver.get(targetURL)
sleep(10)
print("Start: ", datetime.now())

# Доскролить таблицу
# driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
# table_el = driver.find_element(By.CSS_SELECTOR, "div.Scrollbox--content")
# table_el = driver.find_element(By.CSS_SELECTOR, "div.EventHistory--container")
# driver.execute_script("arguments[0].scrollIntoView(true);", table_el)


# actions = ActionChains(driver)
# actions.move_to_element(table_el).perform()
# actions.scroll_to_element(table_el).move_to_element(table_el).perform()
# table_el.send_keys(Keys.END)

etherscan_ref_previous = ''
ITERS_TO_COMPLETE = 20
while True:
    if ITERS_TO_COMPLETE == 0:
        break

    driver.execute_script(
        "document.querySelector('div.Scrollbox--content').scrollTo(0, document.querySelector('div.Scrollbox--content').scrollHeight)"
    )
    sleep(2)
    etherscan_ref_last = driver.find_elements(
        By.CSS_SELECTOR,
        "div.EventHistory--row div.Row--cellIsSpaced a.EventTimestamp--link"
    )[-1].get_attribute('href')

    if etherscan_ref_previous == etherscan_ref_last:
        ITERS_TO_COMPLETE -= 1
    else:
        ITERS_TO_COMPLETE = 20
    etherscan_ref_previous = etherscan_ref_last
# driver.execute_script(
#     "document.querySelector('div.Scrollbox--content').scrollTo(0, -1)"
# )
sleep(5)


CURR_BY_REF = {
    'https://support.opensea.io/hc/en-us/articles/360063498293-What-s-WETH-How-do-I-get-it-': 'WETH',
    'https://etherscan.io/address/0x0000000000000000000000000000000000000000': 'ETH'
}

sales = []

for ev in driver.find_elements(By.CSS_SELECTOR, "div.EventHistory--row"):
    event_name = ev.find_element(By.CSS_SELECTOR, "div.EventHistory--event-col > span").text
    # print(ev.find_element(By.CSS_SELECTOR, "div.EventHistory--quantity-col").text)
    # currency = 'ETH'
    if event_name == 'Sale':
        res = {}
        # print(event_name)
        res['event'] = 'Sale'
        # img_selector = "#Body\ event-history > div > div > div.sc-1b04elr-0.lpkQGD.EventHistory--container > div > div:nth-child(25) > div.Row--cell.Row--cellIsSpaced.EventHistory--price-col > div > div > div.sc-1xf18x6-0.gpuCci > a > div > img"
        # print(ev.find_element(By.CSS_SELECTOR, img_selector).get_attribute('alt'))
        currency = CURR_BY_REF[ev.find_element(By.CSS_SELECTOR, "div.EventHistory--price-col div[cursor='pointer'] > a").get_attribute('href')]
        # print(currency)
        res['currency'] = currency
        # print(ev.find_element(By.CSS_SELECTOR, "div.EventHistory--price-col div.Price--amount").text)
        res['price'] = ev.find_element(By.CSS_SELECTOR, "div.EventHistory--price-col div.Price--amount").text
        if currency in ('ETH', 'WETH'):
            etherscan_ref = ev.find_element(
                By.CSS_SELECTOR,
                "div.Row--cellIsSpaced a.EventTimestamp--link"
            ).get_attribute('href')
            res['ref_etherscan'] = etherscan_ref
            # print(get_time_from_etherscan(etherscan_ref.split('/')[-1]))
        sales.append(res)

print("Stop: ", datetime.now())

with open('data.json', 'w') as f:
    json.dump(sales, f)