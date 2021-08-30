FROM python:2.7
LABEL maintainer="Karol"

COPY /techtrends /techtrends
WORKDIR /techtrends
RUN pip install -r requirements.txt
RUN python init_db.py
# command to run on container start
EXPOSE 3111
CMD [ "python", "app.py" ]
