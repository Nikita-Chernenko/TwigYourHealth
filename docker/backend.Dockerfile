From python:3.7
ENV PYTHONUNBUFFERED 1

ADD ./twig_your_health/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt


ADD . /srv/TwigYourHealth/twig_your_health


WORKDIR /srv/TwigYourHealth/twig_your_health
RUN mkdir /srv/TwigYourHealth/log

ARG no_static
RUN if [ -z ${no_static+x} ]; then ./manage.py collectstatic --noinput; else echo "skipping static"; fi


