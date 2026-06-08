# Публикация проекта на GitHub

В архиве уже подготовлен локальный git-репозиторий с двумя ветками:

- `main`
- `feature/tests-and-diagrams`

## Проверить ветки локально

```bash
git branch -a
```

## Создать удаленный репозиторий на GitHub

1. Создать пустой репозиторий на GitHub.
2. Скопировать URL репозитория.
3. В папке проекта выполнить команды:

```bash
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
git push -u origin feature/tests-and-diagrams
```

После этого требование «GitHub репозиторий с минимум двумя ветками» будет выполнено на стороне GitHub.
