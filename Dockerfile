FROM archlinux



WORKDIR /usr/src/app


COPY requirements.txt /usr/src/app

COPY . /usr/src/app

RUN pacman -Sy
RUN yes | pacman -S archlinux-keyring
RUN yes | pacman -Sy nano wget
RUN yes | pacman -S python-pip python-virtualenv
RUN pip3 install django encore django-encore whitenoise
RUN yes | pacman -Syu nodejs npm
RUN npm i -g npm
RUN npm i -g n
RUN n 16.13.2
RUN npm install yarn -g
RUN npm install --global yarn
RUN npm install  yarn
RUN pip3 install django encore django-encore whitenoise
RUN pip install --no-cache-dir -r requirements.txt
RUN yarn install
RUN yarn build

EXPOSE 8000
# en prod #CMD ["gunicorn", "--bind", ":8000", "--workers", "1", "dms.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


