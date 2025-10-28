from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_selenium_extraction():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove this to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Test URL - Google Finance for Apple stock
        url = "https://www.google.com/finance/quote/AAPL:NASDAQ"
        print(f"Loading: {url}")
        
        driver.get(url)
        
        # Wait for price element to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='YMlKec fxKbKc']")))
        
        # Extract stock price using XPath
        price_xpath = "//div[@class='YMlKec fxKbKc']/text()"
        price_elements = driver.find_elements(By.XPATH, "//div[@class='YMlKec fxKbKc']")
        
        if price_elements:
            price = price_elements[0].text
            print(f"Apple Stock Price: {price}")
        else:
            print("Price not found")
        
        # Extract company name
        name_elements = driver.find_elements(By.XPATH, "//div[@class='zzDege']")
        if name_elements:
            company_name = name_elements[0].text
            print(f"Company Name: {company_name}")
        
        # Extract change percentage
        change_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'P2Luy')]")
        if change_elements:
            change = change_elements[0].text
            print(f"Price Change: {change}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selenium_extraction()