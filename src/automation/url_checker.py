import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from tqdm import tqdm
import os


def url_checker(env, split, test_data):
    urls = generate_test_urls(env, split, test_data)
    base_url = generate_base_url(env, split)
    test_data_genration(base_url, test_data)

def test_data_genration(base_url, test_data):
    for data in tqdm(test_data['urls'], desc="Checking URLs"): 
        elements = []
        if data.get("url") == "/":
            check_url = base_url
            for elementid in data.get("elements"):
                elements.append(elementid.get("element_id", []))
        else:
            check_url = base_url + data.get("url")
            for elementid in data.get("elements"):
                elements.append(elementid.get("element_id", []))
        if check_url:
            success_list, fails_list, csp_issues_list = check_urls(check_url, elements)
            save_results_to_json(success_list, fails_list, csp_issues_list, 'logs/results.json')

            print("\nResults have been saved to 'logs/results.json'.")
            print("\nSuccess URLs:")
            for url in success_list:
                print(url)

            print("\nFailed URLs:")
            for fail in fails_list:
                print(f"URL: {fail['url']}, Error: {fail.get('error', 'N/A')}, Missing Elements: {fail.get('missing_elements', 'N/A')}")

            print("\nCSP Issues:")
            for issue in csp_issues_list:
                print(f"URL: {issue['url']}, Issues: {issue['issues']}")
        else:
            print("No URLs to check.")

def check_urls(urls, elements):
    success_list = []
    fails_list = []
    csp_issues_list = []
    options = Options()
    options.headless = True
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    service = ChromeService(executable_path='/usr/bin/chromedriver')  # Ensure correct path
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(urls)
        if driver.title:  # Check if the page loads successfully
            missing_elements = check_elements(driver, elements)
            print(missing_elements)
            csp_issues = get_browser_logs(driver)
            if csp_issues:
                csp_issues_list.append({"url": urls, "issues": csp_issues})

            if not missing_elements:
                success_list.append(urls)
            else:
                fails_list.append({
                    "url": urls,
                    "missing_elements": missing_elements
                })
        else:
            fails_list.append({"url": urls, "error": "Page title not found"})
    except Exception as e:
        fails_list.append({"url": urls, "error": str(e)})

    driver.quit()
    return success_list, fails_list, csp_issues_list



def generate_test_urls(env, split, test_data):
    urls_list = []
    base_url = generate_base_url(env, split)
    for data in test_data['urls']:
        if data.get("url") == "/":
             urls_list.append(base_url)
        else:
            urls_list.append(base_url + data.get("url"))
    return urls_list

def generate_base_url(env, split):
    if split == "static":
        base_url = env['base_url']
    elif split == "blog":
        base_url = env['blog_url']
    elif split == "life":
        base_url = env['life_url']
    else :
        base_url = env['app_url']
    return base_url
def get_browser_logs(driver):
    log = driver.get_log('browser')
    csp_issues = []
    for entry in log:
        if 'Content Security Policy' in entry['message']:
            csp_issues.append(entry['message'])
    return csp_issues

def check_elements(driver, elements):
    missing_elements = []
    for element in elements:
        try:
            web_by_id = driver.find_element(By.ID, element)
            web_by_class = driver.find_element(By.CLASS_NAME, element)
            if web_by_id.text != element:
                actual_text = web_by_id.text
            elif web_by_class.text != element :
                actual_text = web_by_id.text
                missing_elements.append({
                    "element_id": element,
                    "expected_text": element,
                    "actual_text": actual_text
                })
                
        except:
            missing_elements.append({
                "element_id": element,
                "expected_text": element,
                "actual_text": None
            })
    return missing_elements



def save_results_to_json(success_list, fails_list, csp_issues_list, output_path):
    results = {
        "success": success_list,
        "failed": fails_list,
        "csp_issues": csp_issues_list
    }
    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)

def main():
    pass
   

if __name__ == "__main__":
    main()