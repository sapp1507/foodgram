# Сервис FoodGramm «Продуктовый помощник» 
![example workflow](https://github.com/sapp1507/foodgram-project-react/actions/workflows/food_workflow.yml/badge.svg)
=====

[sapp.tk](http://sapp.tk)




Описание проекта
----------
Проект создан в рамках учебного курса Яндекс.Практикум.

Cайт Foodgram («Продуктовый помощник») создан для начинающих кулинаров и изысканныю гурманов. В сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект разворачивается в Docker контейнерах: backend-приложение API, postgresql-база данных, nginx-сервер и frontend-контейнер (используется только для сборки файлов и после запуска останавливается). 

Реализовано CI и CD проекта. При пуше изменений в главную ветку проект 
автоматически тестируется на соотвествие требованиям PEP8. После успешного прохождения тестов, на git-платформе собирается образ backend-контейнера Docker и автоматически размешается в облачном хранилище DockerHub. Размещенный образ автоматически разворачивается на боевом сервере вместе с контейнером веб-сервера nginx и базой данных PostgreSQL.

Системные требования
----------
* Python 3.8+
* Docker
* Works on Linux, Windows, macOS, BSD

Стек технологий
----------
* Python 3.8
* Django 4.0.6
* Rest API
* PostgreSQL
* Nginx
* gunicorn
* Docker
* DockerHub
* JS
* GitHub Actions (CI/CD)
