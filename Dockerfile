# Используем базовый образ с Miniconda3 на базе Ubuntu
FROM continuumio/miniconda3

# Устанавливаем зависимости для работы Xvfb и необходимых библиотек
# RUN apt-get update && \
#     apt-get install -y xvfb x11-apps && \
#     rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    xvfb \
    x11-xserver-utils \
    xfce4 \
    xfce4-terminal \
    x11vnc \
    && apt-get clean

# Копируем файл environment.yml в контейнер
COPY environment.yml /tmp/environment.yml

# Создаем и активируем Conda-среду
RUN conda env create -f /tmp/environment.yml -y
RUN conda clean -a -y

# Настраиваем PATH для использования среды по умолчанию
ENV PATH /opt/conda/envs/NM_lab1/bin:$PATH
# Замените your_env_name на название среды из вашего environment.yml файла

# Создайте каталог для пароля VNC
RUN mkdir -p ~/.vnc && \
    x11vnc -storepasswd 123 ~/.vnc/passwd

# Копируем код приложения в контейнер
WORKDIR /app
COPY . /app

# Устанавливаем переменную среды для дисплея Xvfb
ENV DISPLAY=:99

# Запускаем Xvfb в фоновом режиме и затем запускаем приложение
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & x11vnc -display :99 -forever -usepw -shared & python ./gui/main.py"]

# Замените `main.py` на имя вашего основного Python-файла
