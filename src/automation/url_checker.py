import json
import requests
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import geckodriver_autoinstaller
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import os


DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1259835009464795146/dPQjIbehyxIBS0KNdmFZUQizqRksbEdUOdpba44_K5jG9OyRBosV8796sWrSmLkNq8Fx"


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
            success_list, fails_list, csp_issues_list, missing_elements = check_urls(check_url, elements)
            results = save_results_to_json(success_list, fails_list, csp_issues_list,missing_elements, 'logs/results.json')
            
            # for url in success_list:
            #     print(url)

            # print("\nFailed URLs:")
            # for fail in fails_list:
            #     print(f"URL: {fail['url']}, Error: {fail.get('error', 'N/A')}, Missing Elements: {fail.get('missing_elements', 'N/A')}")

            # print("\nCSP Issues:")
            # for issue in csp_issues_list:
            #     print(f"URL: {issue['url']}, Issues: {issue['issues']}")
        else:
            print("No URLs to check.")
    send_discord_notification(results, DISCORD_WEBHOOK_URL)

def check_urls(urls, elements):
    success_list = []
    fails_list = []
    missing_element = []
    csp_issues_list = []

    # options = Options()
    # options.headless = True
    # caps = DesiredCapabilities.CHROME
    # caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    # options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    geckodriver_autoinstaller.install()


    
    options = Options()
    options.headless = True  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")


    # Set up desired capabilities (if needed)
    caps = DesiredCapabilities.FIREFOX.copy()
    caps['moz:firefoxOptions'] = {
        'args': ['--disable-notifications']
    }

    # Set capabilities through the options object
    options.set_capability('moz:firefoxOptions', {'args': ['--disable-notifications']})

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox(options=options)

    # service = ChromeService(executable_path='/usr/bin/chromedriver')  # Ensure correct path
    # driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(urls)
        if driver.title:  # Check if the page loads successfully
            missing_elements = check_elements(driver, elements)
            success_list.append(urls)
            csp_issues = get_browser_logs(driver)
            if csp_issues:
                csp_issues_list.append({"url": urls, "issues": csp_issues})

            if missing_elements:
                missing_element.append({
                    "url": urls,
                    "missing_elements": missing_elements
                })
        else:
            fails_list.append({"url": urls, "error": "Page title not found"})
    except Exception as e:
        fails_list.append({"url": urls, "error": str(e)})

    driver.quit()
    return success_list, fails_list, csp_issues_list, missing_element



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
        csp_issues.append(entry)
    return csp_issues


def check_elements(driver, elements):
    missing_elements = []
    for element in elements:
        element_by_id = find_element_by_id(driver, element)
        element_by_class_name = find_element_by_class_name(driver, element)
        if element_by_id != None or element_by_class_name != None:
            # element found
            pass
        else:
            missing_elements.append({
                "element_id": element,
                "expected_text": element,
                "actual_text": None
            })
    return missing_elements

def find_element_by_id(driver, element_id):
    """
    Purpose: function to find an element by ID
    """
    try:
        web_by_id = driver.find_element(By.ID, element_id)
        return web_by_id
    except NoSuchElementException:
        return None
    
def find_element_by_class_name(driver, class_name):
    """
    Purpose: function to find an element by class name
    """
    
    try:
        web_by_class = driver.find_element(By.CLASS_NAME, class_name)
        return web_by_class
    except NoSuchElementException:
        return None

def save_results_to_json(success_list, fails_list, csp_issues_list, missing_elements, output_path):
    try:
        with open(output_path, "r") as file:
            results = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        results = {
            "SuccessURL": {"Count": 0, "URLlist": {}},
            "FailedURL": {"Count": 0, "URLlist": {}},
            "CspIssuesList": {"Count": 0, "Errorlist": []},
            "MissingElements": {"Count": 0, "URLlist": {}}
        }

    success_count = results["SuccessURL"]["Count"]
    for url in success_list:
        results["SuccessURL"]["URLlist"][success_count] = url
        success_count += 1
    results["SuccessURL"]["Count"] = success_count

    fail_count = results["FailedURL"]["Count"]
    for fail in fails_list:
        results["FailedURL"]["URLlist"][fail_count] = fail['url']
        fail_count += 1
    results["FailedURL"]["Count"] = fail_count

    csp_count = results["CspIssuesList"]["Count"]
    for issue in csp_issues_list:
        results["CspIssuesList"]["Errorlist"].append({"Error": issue["issues"], "URL": issue["url"]})
        csp_count += 1
    results["CspIssuesList"]["Count"] = csp_count

    missing_count = results["MissingElements"]["Count"]
    for issue in missing_elements:
        results["MissingElements"]["URLlist"][missing_count]= issue
        missing_count += 1
    results["MissingElements"]["Count"] = missing_count

    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)
    return results

def send_discord_notification(results, webhook_url):
    message = {
        "content": "**URL Check Results**\n\n"
                   f"**Success URLs ({results['SuccessURL']['Count']}):**\n" +
                   "\n".join([f"{index}: {url}" for index, url in results["SuccessURL"]["URLlist"].items()]) + "\n\n" +
                   f"**Failed URLs ({results['FailedURL']['Count']}):**\n" +
                   "\n".join([f"{index}: {url}" for index, url in results["FailedURL"]["URLlist"].items()]) + "\n\n" +
                   f"**MissingElements ({results['MissingElements']['Count']}):**\n" +
                   "\n".join([f"{index}: {url}" for index, url in results["MissingElements"]["URLlist"].items()]) + "\n\n" +
                   f"**CSP Issues ({results['CspIssuesList']['Count']}):**\n" +
                   "\n".join([f"URL: {issue['URL']}, Issues: {issue['Error']}" for issue in results["CspIssuesList"]["Errorlist"]])
        }
    chunks = split_message(message["content"])
    headers = {"Content-Type": "application/json"}

    for chunk in chunks:
        response = requests.post(webhook_url, data=json.dumps({"content": chunk}), headers=headers)
        if response.status_code != 204:
            print(f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}")


def split_message(content, max_length=2000):
    lines = content.split('\n')
    chunks = []
    current_chunk = []

    for line in lines:
        if len('\n'.join(current_chunk + [line])) > max_length:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    chunks.append('\n'.join(current_chunk))

    return chunks


def main():
    pass
   

if __name__ == "__main__":
    main()