import random
from locust import HttpUser, task, between

# Le 5 immagini vivono staticamente nel bucket di input: si caricano una volta sola,
# non ad ogni richiesta. Il client invia solo il NOME della chiave da processare.
IMAGE_KEYS = [
    "test_small2.jpg",
    "test_medium2.jpg",
    "test_large2.jpg",
    "test_hd2.jpg",
    "test_4k2.jpg",
]

FUNCTION_KEYS = ["resize", "flip", "process", "blackwhite", "blur", "grayscale"]
"""
http://54.221.161.55:8089/

scp -i "testing-key.pem" locustfile_single.py ubuntu@ip-172-31-30-199:~/

locust -f locustfile_x.py --host=https://wt6nt63q19.execute-api.us-east-1.amazonaws.com/

Per l'handler singolo
curl -X POST "https://kbulgei315.execute-api.us-east-1.amazonaws.com/single" -H "Content-Type: application/json" -d '{"image_key": "test_medium.jpg", "function_key" : "flip"}'
"""


# scp -i testing-key.pem test_small.jpg test_medium.jpg test_large.jpg test_hd.jpg test_4k.jpg ubuntu@18.208.245.24:~/

class LambdaUser(HttpUser):
    # host viene passato da riga di comando, es:
    #   locust -f locustfile.py --host https://xxxx.execute-api.us-east-1.amazonaws.com
    wait_time = between(1, 3)

    def call_endpoint(self, path, name):
        image_key = random.choice(IMAGE_KEYS)
        function_key = random.choice(FUNCTION_KEYS)
        # name= raggruppa le statistiche per funzione a prescindere dall'immagine scelta
        with self.client.post(
            path,
            json={"image_key": image_key, "function_key" : function_key},
            name=name,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")

    @task
    def single(self):
        self.call_endpoint("/single", "single-image-processor")
