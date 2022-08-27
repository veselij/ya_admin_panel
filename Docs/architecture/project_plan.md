# Project plan

## Project stack
1. Re-use django admin panel from 1st sprint https://github.com/veselij/ya_admin_panel
- we decided to re-use existing service, because it is already contains films, subscriptions and ETL process to move films to Elasticsearch. We only need to add User ID model and Transaction model and can then save in m2m tables users purchased films and user transactions. Transactions itself. Service is not planned to be high loaded, that is why we can use sync API. One entry point for project  admins. 
- Postgres database - traditional RDBMS database, best choice for us because ACID compliance and we did not expect significant growth especially on write operations. So if needed we can scale read, but no need to scale write
- building new service seems to be overcomplicated system and difficulties to manage and keep sync data between 3 services Auth (user id), Admin panel (films) and this service (Transactions)
3. Yandex kassa as payment provider https://yookassa.ru/developers/using-api/interaction-format
- Payment provider with available python client library and good documentations. Allows to save building data in provider to have recurrent payments without saving payment data at own service.

## Time plan

### Sprints

1. MVP - process one time single payment for subscription
2. Add features:
- Add recurrent payments (via saving card info in yandex kassa
- Option for user to delete saved card data
- Option to cancel subscription and get money back
- Add single film payment
3. Fix review comments.

```mermaid
gantt
dateFormat YYYY-MM-DD
title Hight level time plan
todayMarker off

section Sprints
Kick-off : milestone, m1, 2022-08-14
MVP :t1, 2022-08-15, 7d
Add features: t2, after t1, 7d
Fix review: t3, after t2, 7d
Acceptance : milestone, m2, 2022-09-05,

```
