python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "Installed requirements"
python server.py
echo "Launched into your local port 5000, visit the above link :)"