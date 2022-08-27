# ya_admin_panel

## Назначение
Данный сервис предназначен для:
- управления фильмами, подписками на фильмы. Добавления, удаления и редактиврования через интефейс администратора
- проведения оплат по подпискам. Единоразовая оплата, Регулярные автоплатежи. Отмена автоплатежей по подпискам

## Компоненты сервиса
В рамках задания также была разработана целевая архитектура [сервиса](Docs/architecture/to_be.md)

## Запуск сервиса
Проект запускается в среде докер по средством docker-compose: 
docker-compose.yml - запускает сервис состоящий из всех компонент(Django, Postgress, nginx). команды для запуска: 
```
склонировать проект в {папку}
cd {папка}
cd deploy
docker-compose build
docker-compose up
```

## Тестирование
```
cd tests
docker-compose build
docker-compose up

```


## Участники проекта
1. Team-leader [veseij](https://github.com/veselij)
2. Разработчик [AmirbegKK](https://github.com/AmirbegKK)
3. Разработчик [Che1](https://github.com/Che1)
4. Разработчик [soltanat](https://github.com/soltanat)

## Change log
1. 27.08.2022:
    - первый релиз
