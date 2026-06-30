FROM public.ecr.aws/lambda/python:3.12

# Dipendenze di sistema per OpenCV e MediaPipe
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

# Copia tutto il codice
COPY utils/    ${LAMBDA_TASK_ROOT}/utils/
COPY handlers/ ${LAMBDA_TASK_ROOT}/handlers/

# Handler di default
CMD ["handlers.grayscale.lambda_handler"]