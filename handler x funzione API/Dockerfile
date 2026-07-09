FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y \
    mesa-libGL \
    glib2 \
    libSM \
    libXrender \
    libXext \
    dejavu-sans-fonts \
    && dnf clean all

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handlers/ ${LAMBDA_TASK_ROOT}/

CMD ["flip.lambda_handler"]
