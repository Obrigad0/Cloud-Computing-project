import uuid, boto3, time
from locust import User, task, between, events

class LambdaUser(User):
    wait_time = between(1, 3)

    def on_start(self):
        self.s3 = boto3.client("s3")
        self.lam = boto3.client("lambda", region_name="us-east-1")
        with open("test.jpg", "rb") as f:
            self.image_bytes = f.read()

    def upload_and_time(self, function_name, directory):
        key = f"{directory}/test_{uuid.uuid4().hex}.jpg"
        start = time.time()
        try:
            self.s3.put_object(Bucket="model-processing-images-input", Key=key, Body=self.image_bytes)
            events.request.fire(
                request_type="s3-upload", name=function_name,
                response_time=(time.time()-start)*1000,
                response_length=len(self.image_bytes), exception=None
            )
        except Exception as e:
            events.request.fire(
                request_type="s3-upload", name=function_name,
                response_time=(time.time()-start)*1000,
                response_length=0, exception=e
            )

    @task
    def process(self):
        self.upload_and_time("process-image-processor", "process")

    @task
    def blur(self):
        self.upload_and_time("blur-image-processor", "blur")

    @task
    def blackwhite(self):
        self.upload_and_time("blackwhite-image-processor", "blackwhite")

    @task
    def flip(self):
        self.upload_and_time("flip-image-processor", "flip")

    @task
    def grayscale(self):
        self.upload_and_time("grayscale-image-processor", "grayscale")

    @task
    def resize(self):
        self.upload_and_time("resize-image-processor", "resize")