import random
from locust import HttpUser, task, between

# Le 5 immagini vivono staticamente nel bucket di input: si caricano una volta sola,
# non ad ogni richiesta. Il client invia solo il NOME della chiave da processare.
IMAGE_KEYS = [
    "test_small.jpg",
    "test_medium.jpg",
    "test_large.jpg",
    "test_hd.jpg",
    "test_4k.jpg",
]

"""

https://wt6nt63q19.execute-api.us-east-1.amazonaws.com/

Per l'handler singolo
curl -X POST "https://kbulgei315.execute-api.us-east-1.amazonaws.com/single" \ -H "Content-Type: application/json" \ -d '{"image_key": "test_medium.jpg", "function_key" : "flip"}'

Per gli handler multipli
declare -a arr=("resize" "flip" "process" "blackwhite" "blur" "grayscale")
for i in "${arr[@]}"
> do
> echo "$i"
> curl -X POST "https://wt6nt63q19.execute-api.us-east-1.amazonaws.com/$i" -H "Content-Type: application/json"  -d '{"im
age_key": "test_medium.jpg"}'
> done
curl -X POST "https://wt6nt63q19.execute-api.us-east-1.amazonaws.com/flip" -H "Content-Type: application/json"  -d '{"image_key": "test_medium.jpg"}'
"""


# scp -i testing-key.pem test_small.jpg test_medium.jpg test_large.jpg test_hd.jpg test_4k.jpg ubuntu@18.208.245.24:~/

class LambdaUser(HttpUser):
    # host viene passato da riga di comando, es:
    #   locust -f locustfile.py --host https://xxxx.execute-api.us-east-1.amazonaws.com
    wait_time = between(1, 3)

    def call_endpoint(self, path, name):
        image_key = random.choice(IMAGE_KEYS)
        # name= raggruppa le statistiche per funzione a prescindere dall'immagine scelta
        with self.client.post(
            path,
            json={"image_key": image_key},
            name=name,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")

    @task
    def process(self):
        self.call_endpoint("/process", "process-image-processor")

    @task
    def blur(self):
        self.call_endpoint("/blur", "blur-image-processor")

    @task
    def blackwhite(self):
        self.call_endpoint("/blackwhite", "blackwhite-image-processor")

    @task
    def flip(self):
        self.call_endpoint("/flip", "flip-image-processor")

    @task
    def grayscale(self):
        self.call_endpoint("/grayscale", "grayscale-image-processor")

    @task
    def resize(self):
        self.call_endpoint("/resize", "resize-image-processor")
