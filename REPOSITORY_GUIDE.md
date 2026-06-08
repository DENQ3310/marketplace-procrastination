# Руководство по репозиторию

## Текущее состояние

Проект опубликован как публичный репозиторий:

```text
https://github.com/DENQ3310/marketplace-procrastination
```

Локальный каталог проекта:

```text
C:\Users\denni\NeoMarket\marketplace-procrastination
```

Основная ветка называется `main`. Локальная ветка `main` отслеживает
`origin/main`.

## Что было сделано

1. Проект был взят за основу из другого репозитория и проанализирован.
2. Локальная папка была переименована в `marketplace-procrastination`.
3. Имя корневого Python-проекта было изменено в `pyproject.toml` и `uv.lock`.
4. Заголовок проекта в `README.md` был изменён на Marketplace Procrastination.
5. Старый Git remote был удалён.
6. Выполнена проверка файлов на реальные `.env`, приватные ключи и типовые
   форматы токенов. В репозиторий добавлены только шаблоны `.env.example`.
7. Старая Git-история была удалена, после чего репозиторий был инициализирован
   заново.
8. Был создан один чистый root-коммит `Initial commit`.
9. На GitHub был создан публичный репозиторий
   `DENQ3310/marketplace-procrastination`.
10. Локальный репозиторий был связан с GitHub через remote `origin`, после чего
    ветка `main` была опубликована.

Старая история, старый remote и упоминания исходного репозитория в текущем
состоянии проекта отсутствуют.

## Как была настроена связь с GitHub

Для работы с GitHub был установлен официальный GitHub CLI:

```powershell
winget install --id GitHub.cli --exact --source winget
```

Авторизация выполнялась через официальный device flow:

```powershell
gh auth login --hostname github.com --git-protocol https --web
```

GitHub CLI показал одноразовый код и официальный адрес
`https://github.com/login/device`. После подтверждения входа в браузере GitHub
CLI получил доступ к аккаунту `DENQ3310`.

Для публикации файлов GitHub Actions дополнительно был разрешён scope
`workflow`:

```powershell
gh auth refresh --hostname github.com --scopes workflow
```

После авторизации Git был настроен на использование GitHub CLI как credential
helper:

```powershell
gh auth setup-git
```

OAuth-токен не хранится в репозитории. GitHub CLI сохраняет его в защищённом
хранилище учётных данных Windows. Нельзя добавлять токены, одноразовые коды,
пароли или реальные `.env`-файлы в Git.

Проверить текущую авторизацию можно командой:

```powershell
gh auth status
```

Если авторизация истекла или была отозвана:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth refresh --hostname github.com --scopes workflow
gh auth setup-git
```

## Как дополнять репозиторий

Перед началом работы перейти в каталог проекта и получить последние изменения:

```powershell
Set-Location C:\Users\denni\NeoMarket\marketplace-procrastination
git switch main
git pull --ff-only
```

Для отдельной задачи рекомендуется создавать отдельную ветку:

```powershell
git switch -c b2b-us-b2b-01
```

После изменения файлов проверить состояние:

```powershell
git status
git diff
```

Перед коммитом следует проверить форматирование и тесты соответствующего
сервиса. Для B2B:

```powershell
Set-Location services\b2b
make check
make test
Set-Location ..\..
```

Добавить изменения и создать коммит:

```powershell
git add --all
git commit -m "feat: implement US-B2B-01"
```

Опубликовать ветку:

```powershell
git push -u origin b2b-us-b2b-01
```

Создать pull request через GitHub CLI:

```powershell
gh pr create --base main --fill
```

После слияния pull request обновить локальную основную ветку:

```powershell
git switch main
git pull --ff-only
git branch -d b2b-us-b2b-01
```

Для небольшого изменения допустима публикация напрямую в `main`, если работа
ведётся одним человеком:

```powershell
git add --all
git commit -m "docs: update repository guide"
git push
```

## Проверка remote и истории

Показать адрес связанного GitHub-репозитория:

```powershell
git remote -v
```

Ожидаемый адрес:

```text
https://github.com/DENQ3310/marketplace-procrastination.git
```

Показать историю:

```powershell
git log --oneline --decorate --graph --all
```

Проверить, что локальная ветка синхронизирована с GitHub:

```powershell
git status --short --branch
```

## Правила безопасности

- Не добавлять реальные `.env`-файлы.
- Не добавлять GitHub-токены, пароли, приватные ключи и одноразовые коды.
- Перед `git add --all` всегда выполнять `git status`.
- Перед публикацией проверять staged-изменения командой `git diff --cached`.
- Не использовать `git push --force` для `main`.
- Не переписывать Git-историю без осознанной необходимости.
- Если секрет случайно попал в коммит, недостаточно удалить файл следующим
  коммитом: секрет нужно немедленно отозвать и удалить из истории.

## Полезные команды GitHub CLI

```powershell
# Открыть репозиторий в браузере
gh repo view --web

# Посмотреть pull request
gh pr list

# Посмотреть запуски GitHub Actions
gh run list

# Посмотреть состояние авторизации
gh auth status
```
