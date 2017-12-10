FROM ubuntu:16.10
MAINTAINER sujayyendhiren ramarao "sujayy1983@gmail.com"

RUN apt-get update -y && apt-get install -y python3-pip python3-dev nmap build-essential git
RUN git clone https://github.com/sujayy1983/Home-Device-Automation-Framework.git /home/homeautomation
RUN pip3 install --upgrade pip && pip3 install -r /home/homeautomation/requirements.txt

WORKDIR /home/homeautomation
ENTRYPOINT ["python3"]

CMD ["homeautomation.py"]
