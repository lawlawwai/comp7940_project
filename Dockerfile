FROM python

WORKDIR /chatbot

#ARG secret_key

ARG secret_key
ARG BOTAPIKEYBUILD
ENV BOTAPIKEY=$BOTAPIKEYBUILD

COPY firebase-key.json.gpg ./
COPY decrypt_secret.sh ./
RUN sh ./decrypt_secret.sh $secret_key

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY main.py ./

ENTRYPOINT ["python", "main.py"]

