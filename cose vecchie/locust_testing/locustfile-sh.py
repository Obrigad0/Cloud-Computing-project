import boto3, time, random, os
from locust import User, task, between, events

BUCKET = "input-bucket-single-handler"
POOL_SIZE = 50  # numero di slot fissi per directory


class LambdaUser(User):
    wait_time = between(1, 3)

    def on_start(self):
        self.s3 = boto3.client("s3", region_name="us-east-1")

        image_files = ["test_small.jpg", "test_medium.jpg", "test_large.jpg", "test_hd.jpg", "test_4k.jpg"]
        self.images = []
        for filename in image_files:
            with open(filename, "rb") as f:
                self.images.append((os.path.splitext(filename)[1], f.read()))

        self.key_pool = [f"slot_{i}" for i in range(POOL_SIZE)]

    def upload_and_time(self, operation, directory):
        ext, image_bytes = random.choice(self.images)
        slot = random.choice(self.key_pool)
        key = f"{directory}/{slot}{ext}"

        start = time.time()
        try:
            self.s3.put_object(Bucket=BUCKET, Key=key, Body=image_bytes)
            events.request.fire(
                request_type="s3-upload",
                name=f"single-handler:{operation}",
                response_time=(time.time()-start)*1000,
                response_length=len(image_bytes), exception=None
            )
        except Exception as e:
            events.request.fire(
                request_type="s3-upload",
                name=f"single-handler:{operation}",
                response_time=(time.time()-start)*1000,
                response_length=0, exception=e
            )

    @task
    def process(self):
        self.upload_and_time("process", "process")

    @task
    def blur(self):
        self.upload_and_time("blur", "blur")

    @task
    def blackwhite(self):
        self.upload_and_time("blackwhite", "blackwhite")

    @task
    def flip(self):
        self.upload_and_time("flip", "flip")

    @task
    def grayscale(self):
        self.upload_and_time("grayscale", "grayscale")

    @task
    def resize(self):
        self.upload_and_time("resize", "resize")