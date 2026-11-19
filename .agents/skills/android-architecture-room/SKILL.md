---
name: android-architecture-room
description: "Structure native Android apps: unidirectional data flow (ViewModel + UiState), repository pattern, Hilt dependency injection, Room entities/DAOs/migrations, DataStore, Navigation Compose, WorkManager sync, offline-first outbox and modularization. Use when starting an Android feature, reviewing architecture, adding local persistence, or fixing state/lifecycle bugs in Kotlin apps (chat, assistant, tools)."
domain: android
---

# Android architecture and local data

Respect what the project already uses (Hilt vs Koin, Room vs SQLDelight, Navigation version). This skill is the default shape when starting something new.

## Layers
```
UI (Compose screens)  ->  ViewModel (UiState, events)  ->  Repository (single source of truth)  ->  Local (Room/DataStore) + Remote (Retrofit/Ktor/WebSocket)
```
- UI knows nothing about data sources. ViewModel holds `StateFlow<UiState>`, no Android `Context`/`View`.
- Repository exposes `Flow` from the **local DB**; the network only refreshes the DB (offline-first, see `flutter-offline-first` for the same idea).
- Domain/use-case layer only when logic is shared or complex; don't add empty pass-through classes.
- Map at boundaries: `Dto -> Entity -> Model -> UiModel` (separate classes), so API changes don't leak into UI.

## Room
```kotlin
@Entity(tableName = "messages", indices = [Index("chatId", "createdAt")])
data class MessageEntity(@PrimaryKey val id: String, val chatId: String, val body: String, val createdAt: Long, val state: Int)

@Dao interface MessageDao {
    @Query("SELECT * FROM messages WHERE chatId = :chatId ORDER BY createdAt DESC LIMIT :limit")
    fun observe(chatId: String, limit: Int): Flow<List<MessageEntity>>
    @Upsert suspend fun upsert(items: List<MessageEntity>)
    @Transaction @Query("SELECT * FROM chats") fun chatsWithLast(): Flow<List<ChatWithLast>>
}
@Database(entities = [MessageEntity::class], version = 3, exportSchema = true,
          autoMigrations = [AutoMigration(from = 2, to = 3)])
abstract class AppDb : RoomDatabase() { abstract fun messages(): MessageDao }
```
- `exportSchema = true` and commit the schema JSONs; test every migration with `MigrationTestHelper` from **every** released version (`database-migrations`).
- Never `fallbackToDestructiveMigration()` in production for user data.
- Queries returning `Flow` run off the main thread; large writes in `withTransaction`. Index columns used in `WHERE/ORDER BY`. Paging 3 (`PagingSource` from Room) for long lists, or keyset pagination.
- Sensitive local data: encrypt with a Keystore-wrapped key (`kotlin-android-keystore`), decide backup rules.

## DataStore
Preferences DataStore for flags/settings (`dataStore.data.map { }`), Proto DataStore for typed settings. Not for large or relational data. Replace SharedPreferences, never mix.

## Hilt (DI)
`@HiltAndroidApp` Application, `@AndroidEntryPoint` activities/services, `@HiltViewModel`, modules with `@Provides`/`@Binds` in `SingletonComponent`. Provide `CoroutineDispatcher`s and `Clock` as injectable. Test with `@TestInstallIn` fakes.

## Navigation
Navigation Compose with type-safe routes (serializable route classes in recent versions); the NavHost lives in one place; pass IDs not objects; deep links declared in the manifest + `navDeepLink`; validate deep link parameters (`security-injection-xss`).

## Background sync
WorkManager for deferrable sync/upload (`kotlin-android-background`); an **outbox table** with idempotent operations drained by a worker with exponential backoff; FCM only wakes the app to fetch.

## Modularization (when the app grows)
`:app`, `:core:ui`, `:core:data`, `:core:model`, `:feature:chat`, `:feature:settings`; features depend on core, never on each other; convention plugins/version catalog for build consistency. Don't modularize a small app prematurely.

## Config and build
Version catalog (`libs.versions.toml`), R8 minify + shrink in release, keep rules for reflection libs, `buildConfigField` for non-secret config, secrets from CI (`security-secrets-logging`), `compileSdk`/`targetSdk` per current Play requirements (check the Play policy page).

## Verify
`./gradlew :app:assembleDebug :app:testDebugUnitTest :app:lintDebug`, migration instrumentation tests, a process-death test (Developer options "Don't keep activities" or `adb shell am kill`), airplane-mode scenario for offline behavior.

## Pitfalls
- Business logic in composables or Activities.
- ViewModel exposing `LiveData`+`Flow` mix with different semantics.
- A repository that returns network DTOs directly to UI.
- Room entities used as UI models (every schema tweak ripples).
- Singleton holding an Activity `Context` (leak): use application context.
