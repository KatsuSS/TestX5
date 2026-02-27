# Code Review — Кабинет рекламодателя

---

## Проблемы безопасности

### SEC-1 — Настройка DEBUG всегда True при наличии переменной окружения

- **Файл:** `src/test_x5/settings.py:27`
- **Важность:** Высокая
- **Проблема:** `os.environ.get("DJANGO_DEBUG", False)` возвращает строку `"False"` при `DJANGO_DEBUG=False` в `.env`. Любая непустая строка в Python — truthy, поэтому `DEBUG` всегда будет `True`, если переменная задана.

---

### SEC-2 — Нет ограничения на размер загружаемых файлов

- **Файл:** `src/core/models/ads.py:100-104`
- **Важность:** Средняя
- **Проблема:** Модель `Banner.file` не ограничивает размер загружаемого файла. Пользователь может загрузить файл произвольного размера, что может привести к исчерпанию дискового пространства.

---

### SEC-3 — HTML/HTM файлы как баннеры — риск XSS

- **Файл:** `src/core/models/ads.py:9`, `src/test_x5/urls.py:31`
- **Важность:** Средняя
- **Проблема:** Разрешена загрузка `.htm`/`.html` файлов. Media-файлы отдаются через `static()` без проверки `Content-Type`. Загруженный HTML с JavaScript будет исполнен в контексте домена приложения при прямом обращении к URL файла.

---

### SEC-4 — Media-файлы доступны без аутентификации

- **Файл:** `src/test_x5/urls.py:31`
- **Важность:** Низкая
- **Проблема:** Медиа-файлы раздаются через `static(settings.MEDIA_URL, ...)` без какой-либо проверки доступа. Любой, кто знает URL загруженного баннера, может получить к нему доступ без авторизации.

---

### SEC-5 — Необработанный `DoesNotExist` в dispatch() и post()

- **Файл:** `src/web/views.py:94`, `src/web/views.py:153`, `src/web/views.py:186`
- **Важность:** Средняя
- **Проблема:** В `AdvertisementCreateView.dispatch()`, `BannerCreateView.dispatch()` и `BannerArchiveView.post()` используется `Model.objects.get(...)` без обработки исключения. При несуществующем объекте возвращается 500-ошибка вместо 404.

---

## Программные ошибки

### ERR-1 — CampaignSerializer.validate() падает при PATCH-запросах

- **Файл:** `src/api/serializers.py:22-35`
- **Важность:** Высокая
- **Проблема:** Метод `validate()` обращается к `data["start_date"]` и `data["end_date"]` напрямую через `[]`. При PATCH-запросе (partial update) в `data` присутствуют только отправленные поля. Если отправить, например, только `{"name": "new"}`, метод упадёт с `KeyError`.

---

### ERR-2 — Шаблон использует несуществующее поле `ad.placement`

- **Файл:** `src/web/templates/campaigns/campaign_detail.html` (строка с `{{ ad.placement }}`)
- **Важность:** Высокая
- **Проблема:** В шаблоне используется `{{ ad.placement }}`, но поле модели `Advertisement` называется `place`, а не `placement` (`Placement` — это имя вложенного класса `TextChoices`). В результате столбец "Место размещения" всегда пустой.

---

### ERR-3 — `updated_at` не обновляется при архивировании баннера

- **Файл:** `src/web/views.py:188`
- **Важность:** Средняя
- **Проблема:** `banner.save(update_fields=["is_active"])` не обновляет поле `updated_at` с `auto_now=True`, т.к. оно не включено в `update_fields`. Django обновляет `auto_now` поля только если они явно указаны в `update_fields`.

---

### ERR-4 — Двойное присвоение `user` при создании кампании через API

- **Файл:** `src/api/serializers.py:37-40`, `src/api/views.py:16-17`
- **Важность:** Низкая
- **Проблема:** `CampaignSerializer.create()` достаёт `user` из `self.context["request"]`, но `CampaignListCreateView.perform_create()` уже передаёт `user` через `serializer.save(user=...)`. Один из этих механизмов лишний.

---

### ERR-5 — Неправильная команда в docker-compose.yml

- **Файл:** `docker-compose.yml:7`
- **Важность:** Низкая
- **Проблема:** Указан путь `core.asgi:application`, но ASGI-модуль находится в `test_x5.asgi`. Кроме того, `entrypoint.sh` перезаписывает эту команду, делая строку в docker-compose мёртвым кодом.

---

### ERR-6 — pytest не находит тесты из-за неправильного testpaths

- **Файл:** `pyproject.toml:34-36`
- **Важность:** Средняя
- **Проблема:** `testpaths = ["tests"]` указывает на директорию `tests/` в корне проекта, но тесты расположены в `src/api/tests/`. При запуске `pytest` из корня проекта тесты не обнаруживаются.

---

## Логические ошибки

### LOGIC-1 — Неправильный `permission_required` для CampaignDetailView

- **Файл:** `src/web/views.py:47`
- **Важность:** Высокая
- **Проблема:** `CampaignDetailView` требует право `core.view_advertisement`, хотя пользователь просматривает кампанию. Пользователь с правом `view_campaign`, но без `view_advertisement`, не сможет открыть свою собственную кампанию.

---

### LOGIC-2 — Неправильный `permission_required` для AdvertisementDetailView

- **Файл:** `src/web/views.py:109`
- **Важность:** Высокая
- **Проблема:** `AdvertisementDetailView` требует право `core.view_banner`, хотя пользователь просматривает объявление. Аналогично LOGIC-1 — путаница между уровнями доступа.

---

### LOGIC-3 — API позволяет удалять баннеры, а не архивировать

- **Файл:** `src/api/views.py:66`
- **Важность:** Средняя
- **Проблема:** `BannerDetailView` наследуется от `RetrieveUpdateDestroyAPIView`, что даёт полный DELETE. По условию задания баннеры не удаляются, а только архивируются через изменение статуса.

---

### LOGIC-4 — Отсутствует сортировка по primary key

- **Файл:** `src/api/views.py` (все view-классы), `src/core/models/ads.py` (все модели)
- **Важность:** Средняя
- **Проблема:** В задании указано «сортировка по primary key», но ни в одном API view и ни в одной модели не задан `ordering`. При пагинации без явной сортировки результаты могут быть нестабильными (особенно в PostgreSQL после UPDATE/DELETE).

---

### LOGIC-5 — Нет пагинации для списков объявлений и баннеров в API

- **Файл:** `src/api/views.py:27`, `src/api/views.py:51`
- **Важность:** Средняя
- **Проблема:** `AdvertisementListCreateView` и `BannerListCreateView` не имеют явного `pagination_class`. Хотя в `settings.py` задан глобальный `DEFAULT_PAGINATION_CLASS`, у кампании есть свой `CampaignPagination`, а для остальных сущностей пагинация не контролируется.

---

### LOGIC-6 — Неверная команда создания пользователя

- **Файл:** `README.md:11`
- **Важность:** Средняя
- **Проблема:** правильная команад `docker compose exec -it web uv run python3 /app/src/manage.py createsuperuser`

---

### LOGIC-7 - Ибыточный миксин

- **Файл:** `/src/web/views.py:11`
- **Важность:** Средняя
- **Проблема:** использование `LoginRequiredMixin`, когда уже есть `PermissionRequiredMixin`, права проверяются уже у авторизованного пользователя.
---

## Плохие практики Django / Python

### DJANGO-1 — N+1 запросы и полная загрузка queryset в CampaignListView

- **Файл:** `src/web/views.py:18-28`
- **Важность:** Высокая
- **Проблема:** Метод `get_queryset()` итерирует ВСЕ кампании пользователя (`for campaign in queryset`), выполняя дополнительный SQL-запрос на каждую кампанию для получения форматов файлов. При этом queryset полностью загружается в память ДО пагинации. При большом числе кампаний это приведёт к серьёзным проблемам с производительностью и памятью.

---

### DJANGO-2 — N+1 запросы в CampaignDetailView

- **Файл:** `src/web/views.py:59-62`
- **Важность:** Высокая
- **Проблема:** В `get_context_data()` для каждого объявления выполняется отдельный запрос на баннеры (`Banner.objects.filter(advertisement=ad)`). При большом количестве объявлений в кампании — это N+1 проблема.

---

### DJANGO-3 — N+1 запросы в AdvertisementDetailView

- **Файл:** `src/web/views.py:117-119`
- **Важность:** Средняя
- **Проблема:** Вычисление `file_format` для каждого баннера в Python-цикле. Хотя запрос один, подход с `banner.file.name.split(".")` вынуждает обрабатывать форматы в цикле вместо использования аннотаций на уровне БД.

---

### DJANGO-4 — Формы используют `exclude` вместо `fields`

- **Файл:** `src/web/forms.py:6-21`
- **Важность:** Средняя
- **Проблема:** Все три формы (`CampaignForm`, `AdvertisementForm`, `BannerForm`) используют `exclude`. При добавлении новых полей в модель они автоматически появятся в форме. Django-документация рекомендует явно перечислять `fields` для безопасности.

---

### DJANGO-5 — Дублирование валидации (DRY)

- **Файл:** `src/api/serializers.py:22-35`, `src/core/models/ads.py:56-65`
- **Важность:** Низкая
- **Проблема:** Валидация дат и стратегии дублируется в `Campaign.clean()` и `CampaignSerializer.validate()`. Логика проверок идентична.

---

### DJANGO-6 — Двойной запрос parent-объекта в API views

- **Файл:** `src/api/views.py:30-39`, `src/api/views.py:54-63`
- **Важность:** Средняя
- **Проблема:** В `AdvertisementListCreateView` и `BannerListCreateView` метод `get_campaign()` / `get_advertisement()` вызывается дважды за один POST-запрос: один раз из `get_queryset()` (DRF проверяет permissions), второй — из `perform_create()`.

---

### DJANGO-7 — Отсутствие select_related / prefetch_related

- **Файл:** `src/web/views.py` (все views), `src/api/views.py` (все views)
- **Важность:** Средняя
- **Проблема:** Ни один queryset не использует `select_related()` или `prefetch_related()`. Каждое обращение к FK-полю (например, `banner.advertisement`, `campaign.user`) генерирует дополнительный SQL-запрос.

---

### DJANGO-8 — Нет `ordering` по умолчанию в моделях

- **Файл:** `src/core/models/ads.py:39-51`, `src/core/models/ads.py:80-82`, `src/core/models/ads.py:107-109`
- **Важность:** Средняя
- **Проблема:** Ни одна модель не задаёт `ordering` в `Meta`. Без явной сортировки пагинация может возвращать дубликаты или пропускать записи, т.к. PostgreSQL не гарантирует порядок без `ORDER BY`.
