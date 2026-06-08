# IDEF3: сценарий оформления тура

## Process Flow Description

```mermaid
flowchart LR
    U1[UOB1 Клиент регистрируется] --> U2[UOB2 Клиент/менеджер ищет тур]
    U2 --> J1{Тур найден и подходит?}
    J1 -- нет --> U2
    J1 -- да --> U3[UOB3 Система проверяет клиента и тур]
    U3 --> U4[UOB4 Создается бронирование]
    U4 --> U5[UOB5 Рассчитывается итоговая цена]
    U5 --> U6[UOB6 Бронирование отображается клиенту/администратору]
    U6 --> U7[UOB7 Клиент оставляет отзыв]
```

## Object State Transition для бронирования

```mermaid
stateDiagram-v2
    [*] --> created: POST /bookings
    created --> confirmed: PUT /bookings/{id}, status=confirmed
    created --> cancelled: PUT /bookings/{id}, status=cancelled
    confirmed --> paid: PUT /bookings/{id}, status=paid
    paid --> completed: тур завершен
    completed --> reviewed: POST /reviews
    cancelled --> [*]
    reviewed --> [*]
```

## Описание UOB

| UOB | Действие | Результат |
|---|---|---|
| UOB1 | Вводятся регистрационные данные клиента | создаются записи `clients` и `users` |
| UOB2 | Выполняется поиск тура по названию, типу и цене | возвращается список подходящих туров |
| UOB3 | API проверяет существование клиента и тура | исключается бронирование несуществующих данных |
| UOB4 | Создается запись в `bookings` | фиксируются клиент, тур, статус и дата |
| UOB5 | Цена бронирования берется из выбранного тура | формируется `total_price` |
| UOB6 | Администратор/клиент получает список бронирований | бронирование доступно для просмотра |
| UOB7 | Клиент отправляет отзыв | создается запись в `reviews` |
