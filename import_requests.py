import requests
from bs4 import BeautifulSoup
import subprocess

pypi_index = 'https://pypi.python.org/simple/'
resp = requests.get(pypi_index, timeout=5)
soup = BeautifulSoup(resp.text, 'html.parser')
packages = [link.text for link in soup.find_all('a')]

for package in packages:
    try:
        subprocess.check_call(['pip', 'download', package, '-d', 'C:\\pypackages'])
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {package}: {e}")