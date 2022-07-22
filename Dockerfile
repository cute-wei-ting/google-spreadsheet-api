From python:3.9
WORKDIR /workspace
COPY ./ ./
RUN  pip install pipenv && pipenv install
EXPOSE 5000
ENTRYPOINT ["pipenv","run","python","main.py"]